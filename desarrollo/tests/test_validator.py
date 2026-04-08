"""Tests for DataValidator (MVP 1)."""

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
from src.processors.validator import DataValidator


def _make_result(**overrides) -> ScrapedResult:
    """Helper to build a ScrapedResult with defaults."""
    defaults = dict(
        platform=Platform.RAPPI,
        address=Address(
            label="Test", lat=19.43, lng=-99.13, zone_type=ZoneType.CENTRO
        ),
        store_type=StoreType.RESTAURANT,
        store_name="McDonald's",
        items=[
            ScrapedItem(name="Big Mac", original_name="Big Mac", price=145.0),
        ],
        fees=FeeInfo(delivery_fee=0.0, promotions=["Envio Gratis"]),
        time_estimate=TimeEstimate(min_minutes=35, max_minutes=35),
        rating=4.1,
        scrape_layer=ScrapeLayer.DOM,
        success=True,
    )
    defaults.update(overrides)
    return ScrapedResult(**defaults)


class TestValidateResult:
    def test_price_in_range(self):
        """Valid price ($145) passes validation."""
        v = DataValidator()
        result = _make_result()
        vr = v.validate_result(result)
        assert vr.valid
        assert len(vr.suspect_fields) == 0

    def test_price_out_of_range(self):
        """Price > $1000 is flagged as suspect."""
        v = DataValidator()
        result = _make_result(
            items=[ScrapedItem(name="X", original_name="X", price=5000.0)]
        )
        vr = v.validate_result(result)
        assert not vr.valid
        assert any("price" in s for s in vr.suspect_fields)

    def test_price_below_range(self):
        """Price < $1 is flagged as suspect."""
        v = DataValidator()
        result = _make_result(
            items=[ScrapedItem(name="X", original_name="X", price=0.5)]
        )
        vr = v.validate_result(result)
        assert not vr.valid

    def test_fee_out_of_range(self):
        """Fee > $200 is flagged."""
        v = DataValidator()
        result = _make_result(fees=FeeInfo(delivery_fee=500.0))
        vr = v.validate_result(result)
        assert any("delivery_fee" in s for s in vr.suspect_fields)

    def test_failed_result(self):
        """Failed result has 0 completeness."""
        v = DataValidator()
        result = _make_result(success=False)
        vr = v.validate_result(result)
        assert not vr.valid
        assert vr.completeness_score == 0.0


class TestCompletenessScore:
    def test_full_completeness(self):
        """Result with all 5 fields filled gets 1.0."""
        v = DataValidator()
        result = _make_result()
        score = v.get_completeness_score(result)
        assert score == 1.0

    def test_partial_completeness(self):
        """Result missing some fields gets partial score."""
        v = DataValidator()
        result = _make_result(
            fees=FeeInfo(),  # no delivery_fee
            time_estimate=TimeEstimate(),  # no time
            rating=None,  # no rating
        )
        # Only items + promotions filled = 1/5 (items) + 0 + 0 + 0 + 0 = 0.2
        # Wait: FeeInfo() has empty promotions, so promotions = 0
        score = v.get_completeness_score(result)
        assert score == 0.2  # only items filled

    def test_failed_completeness(self):
        """Failed result gets 0.0."""
        v = DataValidator()
        result = _make_result(success=False)
        assert v.get_completeness_score(result) == 0.0

    def test_four_of_five(self):
        """4/5 fields = 0.8 score."""
        v = DataValidator()
        result = _make_result(rating=None)  # missing only rating
        score = v.get_completeness_score(result)
        assert score == 0.8


class TestValidateBatch:
    def test_batch_validation(self):
        """Validate multiple results at once."""
        v = DataValidator()
        results = [_make_result(), _make_result(success=False)]
        vrs = v.validate_batch(results)
        assert len(vrs) == 2
        assert vrs[0].valid
        assert not vrs[1].valid
