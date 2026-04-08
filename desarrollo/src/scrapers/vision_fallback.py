"""VisionFallback: Layer 3 — screenshot + OCR with qwen3-vl."""

import base64
import json
import re
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.ollama_client import OllamaClient

VISION_EXTRACTION_SYSTEM = """Eres un extractor de datos de capturas de pantalla de aplicaciones de delivery de comida en Mexico.
Tu trabajo es leer la imagen y extraer datos estructurados en JSON.
Responde UNICAMENTE con JSON valido, sin explicaciones ni texto adicional.
Todos los precios estan en MXN (pesos mexicanos)."""

VISION_EXTRACTION_USER = """Analiza esta captura de pantalla de {platform_name} y extrae los siguientes datos en formato JSON:

{{
  "restaurant_name": "nombre del restaurante",
  "products": [
    {{
      "name": "nombre del producto tal como aparece",
      "price": 0.00
    }}
  ],
  "delivery_fee": null,
  "delivery_fee_text": "texto original del fee",
  "delivery_time": null,
  "delivery_time_text": "texto original del tiempo",
  "rating": null,
  "promotions": []
}}

Reglas:
- Si un campo no es visible en la imagen, usa null
- delivery_fee y delivery_time son numeros (float y int respectivamente)
- price siempre es float (ej: 145.00, no "$145")
- promotions es una lista de strings con el texto exacto de cada promocion visible
- Si ves varios productos, incluye todos los que puedas leer
- Busca especificamente estos productos si estan visibles: {product_names}"""


class VisionFallback:
    """Layer 3: Extract data from screenshots using vision LLM."""

    def __init__(
        self,
        ollama_client: OllamaClient,
        model: str = "qwen3-vl:8b",
        confidence_threshold: float = 0.7,
        max_retries: int = 2,
    ):
        self.client = ollama_client
        self.model = model
        self.confidence_threshold = confidence_threshold
        self.max_retries = max_retries
        self.logger = get_logger()

    async def extract_from_screenshot(
        self,
        image_path: str,
        platform_name: str = "delivery",
        product_names: list[str] | None = None,
    ) -> dict | None:
        """Extract structured data from a screenshot.

        Returns dict with keys: items, fees, time_estimate, store_name, rating.
        """
        path = Path(image_path)
        if not path.exists():
            self.logger.warning(f"[vision] Screenshot not found: {image_path}")
            return None

        # Read image as base64
        image_b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
        products_str = ", ".join(product_names) if product_names else "cualquier producto"

        prompt = VISION_EXTRACTION_USER.format(
            platform_name=platform_name,
            product_names=products_str,
        )

        for attempt in range(self.max_retries + 1):
            response = await self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": VISION_EXTRACTION_SYSTEM},
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_b64],
                    },
                ],
                format="json",
            )

            if not response:
                self.logger.warning(
                    f"[vision] No response from {self.model} "
                    f"(attempt {attempt + 1})"
                )
                continue

            content = response.get("content", "")
            parsed = self._clean_and_parse(content)

            if parsed and self._validate(parsed):
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

        # Remove markdown fences
        cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Find first { and last }
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
                items.append({
                    "name": p["name"],
                    "original_name": p["name"],
                    "price": float(p["price"]),
                    "category": None,
                    "available": True,
                })

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
