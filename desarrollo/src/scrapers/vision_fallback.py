"""VisionFallback: Layer 3 — screenshot + OCR with Claude vision."""

import json
import re

from src.utils.claude_client import ClaudeClient
from src.utils.logger import get_logger

VISION_SYSTEM = """Eres un extractor de datos de capturas de pantalla de aplicaciones de delivery de comida en Mexico.
Tu trabajo es leer la imagen y extraer datos estructurados en JSON.
Responde UNICAMENTE con JSON valido, sin explicaciones ni texto adicional.
Todos los precios estan en MXN (pesos mexicanos)."""

VISION_PROMPT = """Analiza esta captura de pantalla de {platform_name} y extrae los siguientes datos en formato JSON:

{{
  "restaurant_name": "nombre del restaurante",
  "products": [
    {{"name": "nombre del producto tal como aparece", "price": 0.00}}
  ],
  "delivery_fee": null,
  "delivery_fee_text": "texto original del fee",
  "delivery_time": null,
  "delivery_time_text": "texto original del tiempo",
  "rating": null,
  "promotions": []
}}

Reglas:
- Si un campo no es visible, usa null
- delivery_fee y delivery_time son numeros
- price siempre es float (ej: 145.00, no "$145")
- promotions es una lista de strings
- Busca especificamente: {product_names}

Responde SOLO con el JSON, sin markdown ni explicaciones."""


class VisionFallback:
    """Layer 3: Extract data from screenshots using Claude vision API."""

    def __init__(
        self,
        claude_client: ClaudeClient | None = None,
        max_retries: int = 2,
    ):
        self.client = claude_client or ClaudeClient()
        self.max_retries = max_retries
        self.logger = get_logger()

    async def extract_from_screenshot(
        self,
        image_path: str,
        platform_name: str = "delivery",
        product_names: list[str] | None = None,
    ) -> dict | None:
        """Extract structured data from a screenshot using Claude vision.

        Returns dict with keys: items, fees, time_estimate, store_name, rating.
        """
        if not self.client.is_available():
            self.logger.debug("[vision] Claude API not available, skipping Layer 3")
            return None

        products_str = (
            ", ".join(product_names) if product_names else "cualquier producto"
        )
        prompt = VISION_PROMPT.format(
            platform_name=platform_name,
            product_names=products_str,
        )

        for attempt in range(self.max_retries + 1):
            response_text = await self.client.vision(
                image_path=image_path,
                prompt=prompt,
                system=VISION_SYSTEM,
            )

            if not response_text:
                self.logger.warning(
                    f"[vision] No response from Claude (attempt {attempt + 1})"
                )
                continue

            parsed = self._clean_and_parse(response_text)
            if parsed and self._validate(parsed):
                self.logger.info("[vision] Claude extracted data successfully")
                return self._to_scraper_format(parsed)

            self.logger.warning(
                f"[vision] Invalid response (attempt {attempt + 1})"
            )

        self.logger.warning("[vision] All attempts failed")
        return None

    def _clean_and_parse(self, raw: str) -> dict | None:
        """Clean LLM response and parse JSON."""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip()
        cleaned = re.sub(r"\s*```\s*$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                pass

        return None

    def _validate(self, data: dict) -> bool:
        """Validate extracted data is usable."""
        if not data.get("restaurant_name") and not data.get("products"):
            return False
        products = data.get("products", [])
        if products:
            has_price = any(p.get("price") is not None for p in products)
            if not has_price:
                return False
            for p in products:
                price = p.get("price")
                if price is not None and (price < 1 or price > 5000):
                    return False
        return True

    def _to_scraper_format(self, data: dict) -> dict:
        """Convert vision response to BaseScraper's expected format."""
        items = []
        for p in data.get("products", []):
            if p.get("price") and p.get("name"):
                items.append(
                    {
                        "name": p["name"],
                        "original_name": p["name"],
                        "price": float(p["price"]),
                        "category": None,
                        "available": True,
                    }
                )

        fees = {
            "delivery_fee": data.get("delivery_fee"),
            "delivery_fee_original": data.get("delivery_fee_text"),
            "promotions": data.get("promotions", []),
        }

        time_est = {
            "min_minutes": data.get("delivery_time"),
            "max_minutes": data.get("delivery_time"),
            "original_text": data.get("delivery_time_text"),
        }

        return {
            "items": items,
            "fees": fees,
            "time_estimate": time_est,
            "store_name": data.get("restaurant_name"),
            "rating": data.get("rating"),
        }
