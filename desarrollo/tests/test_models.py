"""Tests for Pydantic schemas (MVP 0)."""

import pytest
from pydantic import ValidationError

from src.models.schemas import (
    Address,
    FeeInfo,
    Platform,
    ScrapeLayer,
    ScrapedItem,
    ScrapedResult,
    ScrapingRun,
    StoreType,
    TimeEstimate,
    ZoneType,
)


# ------------------------------------------------------------------ Address


class TestAddress:
    def test_address_creation(self):
        """Address with valid data creates successfully."""
        addr = Address(
            label="Reforma 222",
            lat=19.4326,
            lng=-99.1332,
            zone_type=ZoneType.CENTRO,
        )
        assert addr.label == "Reforma 222"
        assert addr.lat == 19.4326
        assert addr.lng == -99.1332
        assert addr.zone_type == ZoneType.CENTRO
        assert addr.city == "CDMX"  # default
        assert addr.full_address is None  # default

    def test_address_invalid_lat(self):
        """Address rejects latitude outside [-90, 90]."""
        with pytest.raises(ValidationError):
            Address(
                label="Invalid",
                lat=91.0,
                lng=-99.0,
                zone_type=ZoneType.CENTRO,
            )

    def test_address_invalid_lng(self):
        """Address rejects longitude outside [-180, 180]."""
        with pytest.raises(ValidationError):
            Address(
                label="Invalid",
                lat=19.0,
                lng=-181.0,
                zone_type=ZoneType.CENTRO,
            )

    def test_address_with_full_address(self):
        """Address accepts optional full_address."""
        addr = Address(
            label="Polanco",
            lat=19.4340,
            lng=-99.1956,
            zone_type=ZoneType.PREMIUM,
            full_address="Av. Presidente Masaryk 360, Polanco",
        )
        assert addr.full_address == "Av. Presidente Masaryk 360, Polanco"


# ------------------------------------------------------------------ ScrapedItem


class TestScrapedItem:
    def test_scraped_item_valid(self):
        """ScrapedItem with valid price creates successfully."""
        item = ScrapedItem(
            name="Big Mac",
            original_name="Big Mac Tocino",
            price=155.00,
            category="fast_food",
        )
        assert item.name == "Big Mac"
        assert item.price == 155.00
        assert item.currency == "MXN"  # default
        assert item.available is True  # default

    def test_scraped_item_price_zero_rejected(self):
        """ScrapedItem rejects price <= 0."""
        with pytest.raises(ValidationError):
            ScrapedItem(
                name="Big Mac",
                original_name="Big Mac",
                price=0,
            )

    def test_scraped_item_price_negative_rejected(self):
        """ScrapedItem rejects negative price."""
        with pytest.raises(ValidationError):
            ScrapedItem(
                name="Big Mac",
                original_name="Big Mac",
                price=-10.0,
            )

    def test_scraped_item_price_above_max_rejected(self):
        """ScrapedItem rejects price > 10000."""
        with pytest.raises(ValidationError):
            ScrapedItem(
                name="Big Mac",
                original_name="Big Mac",
                price=10001.0,
            )


# ------------------------------------------------------------------ FeeInfo


class TestFeeInfo:
    def test_fee_info_defaults(self):
        """FeeInfo with no args uses defaults."""
        fee = FeeInfo()
        assert fee.delivery_fee is None
        assert fee.service_fee is None
        assert fee.small_order_fee is None
        assert fee.promotions == []
        assert fee.delivery_fee_original is None

    def test_fee_info_with_values(self):
        """FeeInfo accepts valid fee values."""
        fee = FeeInfo(
            delivery_fee=0.0,
            promotions=["Envio Gratis", "64% OFF"],
            delivery_fee_original="Envio Gratis",
        )
        assert fee.delivery_fee == 0.0
        assert len(fee.promotions) == 2

    def test_fee_info_negative_rejected(self):
        """FeeInfo rejects negative delivery fee."""
        with pytest.raises(ValidationError):
            FeeInfo(delivery_fee=-5.0)


# ------------------------------------------------------------------ Enums


class TestEnums:
    def test_platform_enum(self):
        """Platform has rappi, uber_eats, didi_food."""
        assert Platform.RAPPI.value == "rappi"
        assert Platform.UBER_EATS.value == "uber_eats"
        assert Platform.DIDI_FOOD.value == "didi_food"
        assert len(Platform) == 3

    def test_store_type_enum(self):
        """StoreType has restaurant, convenience, pharmacy."""
        assert StoreType.RESTAURANT.value == "restaurant"
        assert StoreType.CONVENIENCE.value == "convenience"
        assert StoreType.PHARMACY.value == "pharmacy"
        assert len(StoreType) == 3

    def test_zone_type_enum(self):
        """ZoneType has 6 values."""
        assert len(ZoneType) == 6
        assert ZoneType.CENTRO.value == "centro"
        assert ZoneType.EXPANSION.value == "expansion"

    def test_scrape_layer_enum(self):
        """ScrapeLayer has 5 values: api, dom, text_llm, vision, manual."""
        assert len(ScrapeLayer) == 5
        assert ScrapeLayer.API.value == "api"
        assert ScrapeLayer.VISION.value == "vision"


# ------------------------------------------------------------------ TimeEstimate


class TestTimeEstimate:
    def test_time_estimate_defaults(self):
        """TimeEstimate with no args uses defaults."""
        t = TimeEstimate()
        assert t.min_minutes is None
        assert t.max_minutes is None
        assert t.original_text is None

    def test_time_estimate_valid_range(self):
        """TimeEstimate accepts valid minute range."""
        t = TimeEstimate(min_minutes=25, max_minutes=35, original_text="25-35 min")
        assert t.min_minutes == 25
        assert t.max_minutes == 35

    def test_time_estimate_over_180_rejected(self):
        """TimeEstimate rejects minutes > 180."""
        with pytest.raises(ValidationError):
            TimeEstimate(min_minutes=200)


# ------------------------------------------------------------------ ScrapedResult


class TestScrapedResult:
    def test_scraped_result_creation(self, sample_scraped_result):
        """ScrapedResult creates with all fields."""
        r = sample_scraped_result
        assert r.platform == Platform.RAPPI
        assert r.store_name == "McDonald's"
        assert r.success is True
        assert len(r.items) == 1
        assert r.scrape_layer == ScrapeLayer.DOM

    def test_scraped_result_failed(self, sample_address):
        """ScrapedResult with success=False and error message."""
        r = ScrapedResult(
            platform=Platform.RAPPI,
            address=sample_address,
            store_type=StoreType.RESTAURANT,
            store_name="McDonald's",
            scrape_layer=ScrapeLayer.DOM,
            success=False,
            error_message="All layers failed",
        )
        assert r.success is False
        assert r.error_message == "All layers failed"
        assert r.items == []


# ------------------------------------------------------------------ ScrapingRun


class TestScrapingRun:
    def test_scraping_run_empty(self):
        """ScrapingRun with no results has 0% success rate."""
        from datetime import datetime

        run = ScrapingRun(
            run_id="test-001",
            start_time=datetime.now(),
            platforms=[Platform.RAPPI],
            addresses_count=1,
            products_target=["Big Mac"],
        )
        assert run.success_rate == 0.0
        assert run.layer_distribution == {}

    def test_scraping_run_with_results(self, sample_scraped_result):
        """ScrapingRun computes success rate and layer distribution."""
        from datetime import datetime

        run = ScrapingRun(
            run_id="test-002",
            start_time=datetime.now(),
            platforms=[Platform.RAPPI],
            addresses_count=1,
            products_target=["Big Mac"],
            results=[sample_scraped_result],
        )
        assert run.success_rate == 1.0
        assert run.layer_distribution == {"dom": 1}
