"""Tests for DataMerger CSV generation (MVP 1)."""

from datetime import datetime

from src.models.schemas import (
    Address,
    FeeInfo,
    Platform,
    ScrapeLayer,
    ScrapedItem,
    ScrapedResult,
    StoreType,
    TimeEstimate,
    ZoneType,
)
from src.processors.merger import DataMerger


def _make_result(
    platform: Platform = Platform.RAPPI,
    address_label: str = "Reforma 222",
    store_name: str = "McDonald's",
    items: list[ScrapedItem] | None = None,
) -> ScrapedResult:
    """Helper to create a ScrapedResult for testing."""
    if items is None:
        items = [
            ScrapedItem(
                name="Big Mac",
                original_name="Big Mac Tocino",
                price=155.0,
                category="fast_food",
            ),
        ]
    return ScrapedResult(
        platform=platform,
        address=Address(
            label=address_label, lat=19.43, lng=-99.13,
            zone_type=ZoneType.CENTRO,
        ),
        store_type=StoreType.RESTAURANT,
        store_name=store_name,
        items=items,
        fees=FeeInfo(delivery_fee=0.0, promotions=["Envio Gratis"]),
        time_estimate=TimeEstimate(min_minutes=35, max_minutes=35),
        rating=4.1,
        scrape_layer=ScrapeLayer.DOM,
        success=True,
    )


class TestMergeToDataframe:
    def test_merge_single_result(self):
        """1 ScrapedResult with 1 item -> 1 row DataFrame."""
        merger = DataMerger()
        df = merger.merge_to_dataframe([_make_result()])
        assert len(df) == 1
        assert df.iloc[0]["platform"] == "rappi"
        assert df.iloc[0]["canonical_product"] == "Big Mac"
        assert df.iloc[0]["price_mxn"] == 155.0

    def test_merge_multiple_items(self):
        """1 result with 3 items -> 3 rows."""
        items = [
            ScrapedItem(name="Big Mac", original_name="Big Mac", price=155.0),
            ScrapedItem(name="McNuggets", original_name="McNuggets 10", price=145.0),
            ScrapedItem(name="McPollo", original_name="McPollo", price=89.0),
        ]
        merger = DataMerger()
        df = merger.merge_to_dataframe([_make_result(items=items)])
        assert len(df) == 3

    def test_merge_multiple_platforms(self):
        """Results from 2 platforms merge correctly."""
        r1 = _make_result(platform=Platform.RAPPI, address_label="Reforma")
        r2 = _make_result(platform=Platform.UBER_EATS, address_label="Reforma")
        merger = DataMerger()
        df = merger.merge_to_dataframe([r1, r2])
        assert len(df) == 2
        platforms = df["platform"].unique().tolist()
        assert "rappi" in platforms
        assert "uber_eats" in platforms

    def test_csv_columns(self):
        """DataFrame has all expected columns from schema."""
        merger = DataMerger()
        df = merger.merge_to_dataframe([_make_result()])
        expected_cols = [
            "timestamp", "platform", "address_label", "lat", "lng",
            "zone_type", "city", "store_type", "store_name",
            "canonical_product", "original_product_name", "price_mxn",
            "available", "delivery_fee_mxn", "service_fee_mxn",
            "delivery_time_min", "delivery_time_max", "promotions",
            "rating", "scrape_layer",
        ]
        for col in expected_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_failed_result_excluded(self):
        """Failed results are not included in DataFrame."""
        r = _make_result()
        r.success = False
        merger = DataMerger()
        df = merger.merge_to_dataframe([r])
        assert len(df) == 0

    def test_deduplication(self):
        """Same product at same address/platform is deduplicated."""
        r1 = _make_result()
        r2 = _make_result()  # identical
        merger = DataMerger()
        df = merger.merge_to_dataframe([r1, r2])
        assert len(df) == 1

    def test_promotions_joined(self):
        """Promotions list is joined with semicolons."""
        merger = DataMerger()
        df = merger.merge_to_dataframe([_make_result()])
        assert df.iloc[0]["promotions"] == "Envio Gratis"
