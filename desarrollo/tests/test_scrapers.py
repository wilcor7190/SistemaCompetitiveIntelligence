"""Tests for scraper classes (MVP 2)."""

import pytest

from src.config import ScraperConfig
from src.models.schemas import Platform
from src.scrapers.base import BaseScraper
from src.scrapers.didi_food import DiDiFoodScraper, DIDI_FOOD_SELECTORS
from src.scrapers.orchestrator import ScrapingOrchestrator
from src.scrapers.rappi import RappiScraper, RAPPI_SELECTORS
from src.scrapers.uber_eats import UberEatsScraper, UBER_EATS_SELECTORS


def _make_config() -> ScraperConfig:
    return ScraperConfig(
        delay_min=1, delay_max=2, delay_addresses_min=1, delay_addresses_max=2,
        max_retries=1, retry_delay=1, page_load_timeout=10000,
        selector_timeout=5000, screenshot_timeout=3000,
        network_idle_timeout=10000, headless=True, stealth=True,
        user_agent="test", viewport_width=1920, viewport_height=1080,
        locale="es-MX", timezone="America/Mexico_City", geolocation=True,
        circuit_breaker_window=10, circuit_breaker_threshold=0.6,
    )


class TestScraperSelectors:
    def test_rappi_selectors_defined(self):
        """RappiScraper has required selectors."""
        assert "product_card" in RAPPI_SELECTORS or "product_name" in RAPPI_SELECTORS
        assert "delivery_fee" in RAPPI_SELECTORS
        assert "delivery_time" in RAPPI_SELECTORS

    def test_uber_eats_selectors_defined(self):
        """UberEatsScraper has required selectors."""
        assert "product_card" in UBER_EATS_SELECTORS
        assert "delivery_fee" in UBER_EATS_SELECTORS
        assert "arkose_frame" in UBER_EATS_SELECTORS

    def test_didi_food_selectors_defined(self):
        """DiDiFoodScraper has required selectors."""
        assert "product_card" in DIDI_FOOD_SELECTORS
        assert "login_modal" in DIDI_FOOD_SELECTORS


class TestScraperInstantiation:
    def test_base_scraper_abstract(self):
        """BaseScraper cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseScraper(_make_config(), Platform.RAPPI)

    def test_rappi_scraper_creates(self):
        """RappiScraper instantiates correctly."""
        s = RappiScraper(_make_config())
        assert s.platform == Platform.RAPPI
        assert s.get_base_url() == "https://www.rappi.com.mx"

    def test_uber_eats_scraper_creates(self):
        """UberEatsScraper instantiates correctly."""
        s = UberEatsScraper(_make_config())
        assert s.platform == Platform.UBER_EATS
        assert "ubereats.com" in s.get_base_url()

    def test_didi_food_scraper_creates(self):
        """DiDiFoodScraper instantiates correctly."""
        s = DiDiFoodScraper(_make_config())
        assert s.platform == Platform.DIDI_FOOD
        assert "didi-food.com" in s.get_base_url()


class TestScraperFactory:
    def test_factory_rappi(self):
        """Orchestrator creates RappiScraper for RAPPI."""
        from src.config import Config
        config = Config.load()
        orch = ScrapingOrchestrator(config)
        scraper = orch._create_scraper(Platform.RAPPI)
        assert isinstance(scraper, RappiScraper)

    def test_factory_uber_eats(self):
        """Orchestrator creates UberEatsScraper for UBER_EATS."""
        from src.config import Config
        config = Config.load()
        orch = ScrapingOrchestrator(config)
        scraper = orch._create_scraper(Platform.UBER_EATS)
        assert isinstance(scraper, UberEatsScraper)

    def test_factory_didi_food(self):
        """Orchestrator creates DiDiFoodScraper for DIDI_FOOD."""
        from src.config import Config
        config = Config.load()
        orch = ScrapingOrchestrator(config)
        scraper = orch._create_scraper(Platform.DIDI_FOOD)
        assert isinstance(scraper, DiDiFoodScraper)
