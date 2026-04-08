"""Common fixtures for MVP 0 tests."""

import pytest

from src.models.schemas import (
    Address,
    FeeInfo,
    Platform,
    ProductReference,
    ScrapeLayer,
    ScrapedItem,
    ScrapedResult,
    StoreType,
    TimeEstimate,
    ZoneType,
)


@pytest.fixture
def sample_address() -> Address:
    return Address(
        label="Reforma 222 - Centro Historico",
        lat=19.4326,
        lng=-99.1332,
        zone_type=ZoneType.CENTRO,
        city="CDMX",
        full_address="Paseo de la Reforma 222, Juarez, Cuauhtemoc, 06600 CDMX",
    )


@pytest.fixture
def sample_product() -> ProductReference:
    return ProductReference(
        canonical_name="Big Mac",
        aliases=["big mac", "bigmac", "big mac tocino"],
        category="fast_food",
        expected_price_range={"min": 89, "max": 180},
    )


@pytest.fixture
def sample_scraped_item() -> ScrapedItem:
    return ScrapedItem(
        name="Big Mac",
        original_name="Big Mac Tocino",
        price=155.00,
        category="fast_food",
    )


@pytest.fixture
def sample_fee_info() -> FeeInfo:
    return FeeInfo(
        delivery_fee=0.0,
        promotions=["Envio Gratis"],
        delivery_fee_original="Envio Gratis",
    )


@pytest.fixture
def sample_time_estimate() -> TimeEstimate:
    return TimeEstimate(
        min_minutes=35,
        max_minutes=35,
        original_text="35 min",
    )


@pytest.fixture
def sample_scraped_result(
    sample_address: Address,
    sample_scraped_item: ScrapedItem,
    sample_fee_info: FeeInfo,
    sample_time_estimate: TimeEstimate,
) -> ScrapedResult:
    return ScrapedResult(
        platform=Platform.RAPPI,
        address=sample_address,
        store_type=StoreType.RESTAURANT,
        store_name="McDonald's",
        store_id="1306705702",
        items=[sample_scraped_item],
        fees=sample_fee_info,
        time_estimate=sample_time_estimate,
        scrape_layer=ScrapeLayer.DOM,
        success=True,
    )
