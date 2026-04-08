"""ProductMatcher: match scraped product names to canonical names."""

import math

from src.models.schemas import ProductReference
from src.utils.logger import get_logger
from src.utils.ollama_client import OllamaClient


class ProductMatcher:
    """Matches product names using aliases and optionally embeddings."""

    def __init__(
        self,
        products: list[ProductReference],
        ollama_client: OllamaClient | None = None,
        embedding_model: str = "nomic-embed-text",
        similarity_threshold: float = 0.85,
    ):
        self.products = products
        self.ollama = ollama_client
        self.embedding_model = embedding_model
        self.threshold = similarity_threshold
        self.logger = get_logger()

        # Build alias lookup: normalized alias → canonical name
        self._alias_map: dict[str, str] = {}
        for prod in products:
            for alias in prod.aliases:
                self._alias_map[self._normalize(alias)] = prod.canonical_name
            self._alias_map[self._normalize(prod.canonical_name)] = prod.canonical_name

        # Embedding cache: text → vector
        self._embed_cache: dict[str, list[float]] = {}

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

    async def match_product_with_embeddings(
        self, original_name: str
    ) -> str | None:
        """Match using embeddings when alias fails. Requires Ollama."""
        # First try alias
        result = self.match_product(original_name)
        if result:
            return result

        # Try embeddings if Ollama available
        if not self.ollama:
            return None

        original_embed = await self._get_embedding(original_name)
        if not original_embed:
            return None

        best_match = None
        best_score = 0.0

        for prod in self.products:
            canonical_embed = await self._get_embedding(prod.canonical_name)
            if not canonical_embed:
                continue
            score = self._cosine_similarity(original_embed, canonical_embed)
            if score > best_score:
                best_score = score
                best_match = prod.canonical_name

        if best_score >= self.threshold and best_match:
            self.logger.debug(
                f"Embedding match: '{original_name}' → '{best_match}' "
                f"(score={best_score:.3f})"
            )
            return best_match

        return None

    async def _get_embedding(self, text: str) -> list[float] | None:
        """Get embedding with cache."""
        if text in self._embed_cache:
            return self._embed_cache[text]

        if not self.ollama:
            return None

        embedding = await self.ollama.embed(self.embedding_model, text)
        if embedding:
            self._embed_cache[text] = embedding
        return embedding

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
