"""ProductMatcher: match scraped product names to canonical names."""

import math

from src.models.schemas import ProductReference
from src.utils.logger import get_logger


class ProductMatcher:
    """Matches product names using normalized alias lookup."""

    def __init__(
        self,
        products: list[ProductReference],
        similarity_threshold: float = 0.85,
    ):
        self.products = products
        self.threshold = similarity_threshold
        self.logger = get_logger()

        # Build alias lookup: normalized alias → canonical name
        self._alias_map: dict[str, str] = {}
        for prod in products:
            for alias in prod.aliases:
                self._alias_map[self._normalize(alias)] = prod.canonical_name
            self._alias_map[self._normalize(prod.canonical_name)] = prod.canonical_name

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for matching: lowercase, remove hyphens/special chars."""
        return text.strip().lower().replace("-", " ").replace("_", " ")

    def match_product(self, original_name: str) -> str | None:
        """Match a product name to its canonical name.

        Step 1: Exact alias match (normalized).
        Step 2: Partial match — alias contained in name.
        Step 3: Partial match — name contained in alias.
        Returns canonical name or None if no match.
        """
        name_norm = self._normalize(original_name)

        # Step 1: Exact alias match
        if name_norm in self._alias_map:
            return self._alias_map[name_norm]

        # Step 2: Check if any alias is contained in the name
        for alias, canonical in self._alias_map.items():
            if alias in name_norm:
                return canonical

        # Step 3: Check if the product name is contained in any alias
        for alias, canonical in self._alias_map.items():
            if name_norm in alias:
                return canonical

        return None

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
