"""TextParser: Layer 2 fallback — parse raw text with Claude API."""

import json
import re

from src.utils.claude_client import ClaudeClient
from src.utils.logger import get_logger

TEXT_PARSER_SYSTEM = """Eres un parser de datos de texto crudo extraido de paginas web de delivery de comida en Mexico.
Recibes texto sin formato (copiado de una pagina web) y debes extraer datos estructurados.
Responde UNICAMENTE con JSON valido. Todos los precios en MXN."""

TEXT_PARSER_PROMPT = """Extrae datos estructurados del siguiente texto crudo de {platform_name}:

---
{raw_text}
---

Responde con este formato JSON:
{{
  "restaurant_name": "nombre si lo encuentras",
  "products": [{{"name": "nombre del producto", "price": 0.00}}],
  "delivery_fee": null,
  "delivery_time_min": null,
  "delivery_time_max": null,
  "rating": null,
  "promotions": []
}}

Reglas:
- Busca patrones de precio como "$XX.XX", "MXN XX"
- Si no encuentras un campo, usa null
- Busca especificamente: {product_names}

Responde SOLO con el JSON, sin markdown."""


class TextParser:
    """Layer 2 fallback: parse raw page text using Claude API."""

    def __init__(
        self,
        claude_client: ClaudeClient | None = None,
        max_retries: int = 2,
    ):
        self.client = claude_client or ClaudeClient()
        self.max_retries = max_retries
        self.logger = get_logger()

    async def parse_raw_text(
        self,
        raw_text: str,
        platform_name: str = "delivery",
        product_names: list[str] | None = None,
    ) -> dict | None:
        """Parse raw text into structured data."""
        if not raw_text or len(raw_text.strip()) < 20:
            return None

        if not self.client.is_available():
            return self._regex_fallback(raw_text)

        text = raw_text[:3000]
        products_str = (
            ", ".join(product_names) if product_names else "cualquier producto"
        )
        prompt = TEXT_PARSER_PROMPT.format(
            platform_name=platform_name,
            raw_text=text,
            product_names=products_str,
        )

        for attempt in range(self.max_retries + 1):
            response = await self.client.chat(
                prompt=prompt, system=TEXT_PARSER_SYSTEM
            )
            if not response:
                continue

            parsed = self._clean_and_parse(response)
            if parsed:
                return self._to_scraper_format(parsed)

            self.logger.debug(f"[text_parser] Invalid JSON (attempt {attempt + 1})")

        return self._regex_fallback(raw_text)

    def _clean_and_parse(self, raw: str) -> dict | None:
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

    def _to_scraper_format(self, data: dict) -> dict | None:
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

        if not items:
            return None

        return {
            "items": items,
            "fees": {
                "delivery_fee": data.get("delivery_fee"),
                "promotions": data.get("promotions", []),
            },
            "time_estimate": {
                "min_minutes": data.get("delivery_time_min"),
                "max_minutes": data.get("delivery_time_max"),
            },
            "store_name": data.get("restaurant_name"),
            "rating": data.get("rating"),
        }

    def _regex_fallback(self, text: str) -> dict | None:
        """Last resort: extract prices with regex."""
        pattern = r'["\']?([^"\'$\n]{3,40})["\']?\s*[\$:]\s*(\d+\.?\d{0,2})'
        items = []
        for match in re.finditer(pattern, text):
            name = match.group(1).strip()
            price = float(match.group(2))
            if 1 < price < 1000:
                items.append(
                    {
                        "name": name,
                        "original_name": name,
                        "price": price,
                        "category": None,
                        "available": True,
                    }
                )

        if items:
            self.logger.info(
                f"[text_parser] Regex fallback extracted {len(items)} items"
            )
            return {"items": items, "fees": {}, "time_estimate": {}}

        return None
