"""Integration tests with mock data (MVP 2)."""

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
from src.processors.normalizer import DataNormalizer
from src.processors.product_matcher import ProductMatcher
from src.processors.validator import DataValidator


def _make_result(
    platform: Platform,
    address_label: str,
    price: float,
    product_name: str = "Big Mac",
    store_name: str = "McDonald's",
) -> ScrapedResult:
    return ScrapedResult(
        platform=platform,
        address=Address(
            label=address_label, lat=19.43, lng=-99.13,
            zone_type=ZoneType.CENTRO,
        ),
        store_type=StoreType.RESTAURANT,
        store_name=store_name,
        items=[
            ScrapedItem(
                name=product_name,
                original_name=product_name,
                price=price,
                category="fast_food",
            ),
        ],
        fees=FeeInfo(delivery_fee=0.0),
        time_estimate=TimeEstimate(min_minutes=30, max_minutes=40),
        rating=4.2,
        scrape_layer=ScrapeLayer.DOM,
        success=True,
    )


class TestFullPipelineMock:
    def test_full_pipeline(self):
        """Mock scraping -> normalize -> validate -> merge -> CSV."""
        results = [
            _make_result(Platform.RAPPI, "Reforma 222", 155.0),
            _make_result(Platform.UBER_EATS, "Reforma 222", 145.0),
        ]

        # Normalize (no matcher needed for this test)
        normalizer = DataNormalizer()
        normalizer.normalize_results(results)

        # Validate
        validator = DataValidator()
        validations = validator.validate_batch(results)
        assert all(v.valid for v in validations)

        # Merge
        merger = DataMerger(validator)
        df = merger.merge_to_dataframe(results)

        assert len(df) == 2
        assert set(df["platform"].tolist()) == {"rappi", "uber_eats"}
        assert df[df["platform"] == "rappi"].iloc[0]["price_mxn"] == 155.0
        assert df[df["platform"] == "uber_eats"].iloc[0]["price_mxn"] == 145.0


class TestMultiPlatformMerge:
    def test_three_platforms_merge(self):
        """Data from 3 platforms merges correctly."""
        results = [
            _make_result(Platform.RAPPI, "Reforma", 155.0),
            _make_result(Platform.UBER_EATS, "Reforma", 145.0),
            _make_result(Platform.DIDI_FOOD, "Reforma", 150.0),
        ]
        merger = DataMerger()
        df = merger.merge_to_dataframe(results)

        assert len(df) == 3
        platforms = set(df["platform"].tolist())
        assert platforms == {"rappi", "uber_eats", "didi_food"}

    def test_same_product_different_platforms(self):
        """Same product at same address from different platforms are separate rows."""
        results = [
            _make_result(Platform.RAPPI, "Polanco", 155.0, "Big Mac"),
            _make_result(Platform.UBER_EATS, "Polanco", 145.0, "Big Mac"),
        ]
        merger = DataMerger()
        df = merger.merge_to_dataframe(results)

        assert len(df) == 2
        prices = sorted(df["price_mxn"].tolist())
        assert prices == [145.0, 155.0]

    def test_multiple_addresses_multiple_platforms(self):
        """Multiple addresses x multiple platforms generate correct rows."""
        results = [
            _make_result(Platform.RAPPI, "Reforma", 155.0),
            _make_result(Platform.RAPPI, "Polanco", 160.0),
            _make_result(Platform.UBER_EATS, "Reforma", 145.0),
            _make_result(Platform.UBER_EATS, "Polanco", 150.0),
        ]
        merger = DataMerger()
        df = merger.merge_to_dataframe(results)

        assert len(df) == 4
        assert df["address_label"].nunique() == 2
        assert df["platform"].nunique() == 2


class TestDeduplication:
    def test_same_product_same_address_same_platform_deduped(self):
        """Duplicate entries are removed (keep first)."""
        results = [
            _make_result(Platform.RAPPI, "Reforma", 155.0),
            _make_result(Platform.RAPPI, "Reforma", 160.0),  # duplicate key
        ]
        merger = DataMerger()
        df = merger.merge_to_dataframe(results)

        # Should keep first (155.0), drop second (160.0)
        assert len(df) == 1
        assert df.iloc[0]["price_mxn"] == 155.0

    def test_different_products_not_deduped(self):
        """Different products at same address/platform are kept."""
        r = ScrapedResult(
            platform=Platform.RAPPI,
            address=Address(
                label="Reforma", lat=19.43, lng=-99.13,
                zone_type=ZoneType.CENTRO,
            ),
            store_type=StoreType.RESTAURANT,
            store_name="McDonald's",
            items=[
                ScrapedItem(name="Big Mac", original_name="Big Mac", price=155.0),
                ScrapedItem(name="McNuggets", original_name="McNuggets", price=145.0),
            ],
            fees=FeeInfo(delivery_fee=0.0),
            time_estimate=TimeEstimate(min_minutes=35, max_minutes=35),
            scrape_layer=ScrapeLayer.DOM,
            success=True,
        )
        merger = DataMerger()
        df = merger.merge_to_dataframe([r])

        assert len(df) == 2


class TestFailedResults:
    def test_failed_results_excluded(self):
        """Failed results don't appear in merged data."""
        success = _make_result(Platform.RAPPI, "Reforma", 155.0)
        failed = _make_result(Platform.UBER_EATS, "Reforma", 0.1)
        failed.success = False

        merger = DataMerger()
        df = merger.merge_to_dataframe([success, failed])

        assert len(df) == 1
        assert df.iloc[0]["platform"] == "rappi"
