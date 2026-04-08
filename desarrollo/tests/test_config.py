"""Tests for config loader (MVP 0)."""

from src.config import Config, OllamaConfig, ScraperConfig
from src.models.schemas import Platform, StoreType


class TestConfigLoadAddresses:
    def test_load_addresses(self):
        """Config loads addresses.json with 25 addresses."""
        config = Config.load()
        addresses = config.get_addresses()
        assert len(addresses) == 25

    def test_addresses_have_required_fields(self):
        """Each address has label, lat, lng, zone_type."""
        config = Config.load()
        for addr in config.get_addresses():
            assert addr.label
            assert -90 <= addr.lat <= 90
            assert -180 <= addr.lng <= 180
            assert addr.zone_type is not None

    def test_addresses_cover_5_zone_types(self):
        """Addresses cover centro, premium, residencial, periferia, corporativo."""
        config = Config.load()
        zone_types = {a.zone_type.value for a in config.get_addresses()}
        expected = {"centro", "premium", "residencial", "periferia", "corporativo"}
        assert expected.issubset(zone_types)


class TestConfigLoadProducts:
    def test_load_products(self):
        """Config loads products.json with 3 store_groups."""
        config = Config.load()
        store_groups = config.get_store_groups()
        assert len(store_groups) == 3

    def test_store_group_types(self):
        """Store groups cover restaurant, convenience, pharmacy."""
        config = Config.load()
        types = {sg.store_type for sg in config.get_store_groups()}
        assert types == {
            StoreType.RESTAURANT,
            StoreType.CONVENIENCE,
            StoreType.PHARMACY,
        }

    def test_restaurant_has_3_products(self):
        """Restaurant store group has 3 products (Big Mac, McNuggets, Combo)."""
        config = Config.load()
        restaurant = next(
            sg for sg in config.get_store_groups()
            if sg.store_type == StoreType.RESTAURANT
        )
        assert len(restaurant.products) == 3
        names = [p.canonical_name for p in restaurant.products]
        assert "Big Mac" in names
        assert "McNuggets 10 pzas" in names
        assert "Combo Mediano" in names

    def test_all_products_have_aliases(self):
        """Every product has at least 1 alias."""
        config = Config.load()
        for product in config.get_products():
            assert len(product.aliases) >= 1, (
                f"{product.canonical_name} has no aliases"
            )

    def test_all_products_have_price_range(self):
        """Every product has expected_price_range with min and max."""
        config = Config.load()
        for product in config.get_products():
            assert "min" in product.expected_price_range
            assert "max" in product.expected_price_range
            assert product.expected_price_range["min"] < product.expected_price_range["max"]


class TestConfigLoadSettings:
    def test_load_settings(self):
        """Config loads settings.yaml with scraping config."""
        config = Config.load()
        sc = config.get_scraper_config()
        assert isinstance(sc, ScraperConfig)
        assert sc.delay_min > 0
        assert sc.delay_max > sc.delay_min
        assert sc.max_retries >= 1
        assert sc.page_load_timeout > 0

    def test_platforms_from_settings(self):
        """Settings lists 3 platforms in correct order."""
        config = Config.load()
        platforms = config.get_platforms()
        assert len(platforms) == 3
        assert platforms[0] == Platform.RAPPI  # ADR-001: Rappi first
        assert platforms[1] == Platform.UBER_EATS
        assert platforms[2] == Platform.DIDI_FOOD

    def test_ollama_config(self):
        """Ollama config loads with expected models."""
        config = Config.load()
        oc = config.get_ollama_config()
        assert isinstance(oc, OllamaConfig)
        assert "localhost" in oc.base_url
        assert oc.model_vision == "qwen3-vl:8b"
        assert oc.model_embeddings == "nomic-embed-text"
        assert 0 < oc.embedding_similarity_threshold <= 1.0

    def test_browser_config(self):
        """Browser config has headless and stealth settings."""
        config = Config.load()
        sc = config.get_scraper_config()
        assert isinstance(sc.headless, bool)
        assert isinstance(sc.stealth, bool)
        assert sc.viewport_width == 1920
        assert sc.viewport_height == 1080
        assert sc.locale == "es-MX"

    def test_paths_config(self):
        """Paths config has expected keys."""
        config = Config.load()
        paths = config.get_paths()
        assert "raw_data" in paths
        assert "merged_data" in paths
        assert "screenshots" in paths
        assert "reports" in paths
