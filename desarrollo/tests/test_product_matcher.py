"""Tests for ProductMatcher alias matching (MVP 1)."""

from src.models.schemas import ProductReference
from src.processors.product_matcher import ProductMatcher


def _make_matcher() -> ProductMatcher:
    """Create a matcher with test products."""
    products = [
        ProductReference(
            canonical_name="Big Mac",
            aliases=["big mac", "bigmac", "big mac tocino", "big mac individual"],
            category="fast_food",
            expected_price_range={"min": 89, "max": 180},
        ),
        ProductReference(
            canonical_name="McNuggets 10 pzas",
            aliases=["mcnuggets 10 pzas", "mcnuggets 10 piezas", "10 mcnuggets",
                     "chicken mcnuggets 10", "nuggets 10", "mcnuggets 10"],
            category="fast_food",
            expected_price_range={"min": 100, "max": 200},
        ),
        ProductReference(
            canonical_name="Combo Mediano",
            aliases=["mctrio mediano", "mctrio", "combo big mac",
                     "mctrio hamb c/queso", "mctrio hamb dbl"],
            category="fast_food",
            expected_price_range={"min": 85, "max": 200},
        ),
    ]
    return ProductMatcher(products)


class TestMatchByAlias:
    def test_match_exact_alias(self):
        m = _make_matcher()
        assert m.match_product("big mac") == "Big Mac"

    def test_match_variant(self):
        m = _make_matcher()
        assert m.match_product("big mac tocino") == "Big Mac"

    def test_match_canonical_name(self):
        m = _make_matcher()
        assert m.match_product("Big Mac") == "Big Mac"

    def test_match_case_insensitive(self):
        m = _make_matcher()
        assert m.match_product("BIG MAC") == "Big Mac"

    def test_match_contained_in_name(self):
        """Alias found inside a longer product name."""
        m = _make_matcher()
        assert m.match_product("McTrío mediano Big Mac Tocino") == "Big Mac"

    def test_match_mcnuggets(self):
        m = _make_matcher()
        assert m.match_product("mcnuggets 10 pzas") == "McNuggets 10 pzas"

    def test_match_mcnuggets_variant(self):
        m = _make_matcher()
        assert m.match_product("McNuggets de Pollo 10 pzas") is None  # not in aliases

    def test_match_combo(self):
        m = _make_matcher()
        assert m.match_product("mctrio mediano") == "Combo Mediano"

    def test_no_match(self):
        m = _make_matcher()
        assert m.match_product("McFlurry Oreo") is None

    def test_no_match_unrelated(self):
        m = _make_matcher()
        assert m.match_product("Coca-Cola 600ml") is None


class TestCosine:
    def test_cosine_identical(self):
        vec = [1.0, 2.0, 3.0]
        assert ProductMatcher._cosine_similarity(vec, vec) > 0.99

    def test_cosine_orthogonal(self):
        v1 = [1.0, 0.0]
        v2 = [0.0, 1.0]
        assert abs(ProductMatcher._cosine_similarity(v1, v2)) < 0.01

    def test_cosine_zero_vector(self):
        v1 = [0.0, 0.0]
        v2 = [1.0, 2.0]
        assert ProductMatcher._cosine_similarity(v1, v2) == 0.0
