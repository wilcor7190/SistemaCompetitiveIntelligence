"""DataNormalizer: parse prices, fees, times and match products."""

import re

from src.models.schemas import ScrapedItem, ScrapedResult
from src.processors.product_matcher import ProductMatcher
from src.utils.logger import get_logger


class DataNormalizer:
    """Normalizes raw scraped data: prices, fees, times, product names."""

    def __init__(self, product_matcher: ProductMatcher | None = None):
        self.matcher = product_matcher
        self.logger = get_logger()

    def normalize_results(self, results: list[ScrapedResult]) -> list[ScrapedResult]:
        """Normalize all results: match product names to canonical."""
        for result in results:
            if not result.success:
                continue
            result.items = self._normalize_items(result.items)
        return results

    def _normalize_items(self, items: list[ScrapedItem]) -> list[ScrapedItem]:
        """Normalize product names using matcher."""
        if not self.matcher:
            return items
        for item in items:
            canonical = self.matcher.match_product(item.original_name)
            if canonical:
                item.name = canonical
        return items

    # ------------------------------------------------------------------
    # Static parsing utilities
    # ------------------------------------------------------------------

    @staticmethod
    def parse_price(text: str | None) -> float | None:
        """Convert price text to float MXN.

        Handles: '$145.00', '$ 155', 'MXN 79', '139-149' (takes min),
        '$129 $155' (takes min/discounted), 'Gratis' → 0.0, '' → None.
        """
        if not text or not text.strip():
            return None

        text = text.strip()

        if text.lower() in (
            "gratis",
            "envio gratis",
            "envío gratis",
            "free",
            "$0",
            "$0.00",
        ):
            return 0.0

        if any(kw in text.lower() for kw in ("no disponible", "agotado", "n/a")):
            return None

        numbers = re.findall(r"(\d[\d,]*\.?\d*)", text.replace(",", ""))
        if not numbers:
            return None

        prices = [float(n) for n in numbers]
        return min(prices)

    @staticmethod
    def parse_fee(text: str | None) -> float | None:
        """Parse delivery fee text. 'Gratis' → 0.0."""
        if not text or not text.strip():
            return None
        if "gratis" in text.lower() or "free" in text.lower():
            return 0.0
        return DataNormalizer.parse_price(text)

    @staticmethod
    def parse_delivery_time(text: str | None) -> tuple[int | None, int | None]:
        """Convert time text to (min_minutes, max_minutes).

        Handles: '35 min', '25-35 min', '20-30 minutos', 'Llega en 35 min'.
        """
        if not text or not text.strip():
            return (None, None)

        range_match = re.search(r"(\d+)\s*[-–]\s*(\d+)", text)
        if range_match:
            return (int(range_match.group(1)), int(range_match.group(2)))

        single_match = re.search(r"(\d+)", text)
        if single_match:
            value = int(single_match.group(1))
            return (value, value)

        return (None, None)

    @staticmethod
    def parse_promotions(texts: list[str]) -> list[str]:
        """Filter texts that look like promotions."""
        promo_keywords = [
            "gratis",
            "free",
            "off",
            "descuento",
            "2x1",
            "3x2",
            "promo",
            "oferta",
            "ahorra",
            "especial",
            "cupón",
            "cupon",
        ]
        promotions = []
        for text in texts:
            text_lower = text.strip().lower()
            if any(kw in text_lower for kw in promo_keywords):
                promotions.append(text.strip())
        return promotions
