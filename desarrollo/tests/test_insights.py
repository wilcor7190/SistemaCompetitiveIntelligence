"""Tests for InsightGenerator (MVP 3)."""

import pytest

import pandas as pd

from src.analysis.insights import DIMENSIONS, Insight, InsightGenerator


@pytest.fixture
def sample_df():
    """Sample DataFrame with multi-platform data."""
    return pd.DataFrame({
        "platform": ["rappi", "rappi", "uber_eats", "uber_eats"],
        "address_label": ["Reforma", "Polanco", "Reforma", "Polanco"],
        "zone_type": ["centro", "premium", "centro", "premium"],
        "canonical_product": ["Big Mac", "Big Mac", "Big Mac", "Big Mac"],
        "original_product_name": ["Big Mac Tocino", "Big Mac", "Big Mac", "Big Mac"],
        "price_mxn": [155.0, 160.0, 145.0, 150.0],
        "delivery_fee_mxn": [0.0, 0.0, 4.99, 4.99],
        "delivery_time_min": [35, 35, 25, 30],
        "delivery_time_max": [35, 35, 35, 40],
        "promotions": ["Envio Gratis", "Envio Gratis", "", ""],
        "rating": [4.1, 4.1, 4.5, 4.5],
        "scrape_layer": ["dom", "dom", "dom", "dom"],
        "store_type": ["restaurant"] * 4,
        "store_name": ["McDonald's"] * 4,
    })


class TestDimensions:
    def test_5_dimensions_defined(self):
        """There are exactly 5 insight dimensions."""
        assert len(DIMENSIONS) == 5

    def test_dimensions_include_required(self):
        """All 5 brief dimensions are present."""
        assert "Posicionamiento de Precios" in DIMENSIONS
        assert "Ventaja Operacional" in DIMENSIONS
        assert "Estructura de Fees" in DIMENSIONS
        assert "Estrategia Promocional" in DIMENSIONS
        assert "Variabilidad Geografica" in DIMENSIONS


class TestInsightGeneration:
    @pytest.mark.asyncio
    async def test_generates_5_insights(self, sample_df):
        """Generator produces exactly 5 insights."""
        gen = InsightGenerator()
        insights = await gen.generate_insights(sample_df)
        assert len(insights) == 5

    @pytest.mark.asyncio
    async def test_each_insight_has_fields(self, sample_df):
        """Each insight has number, title, dimension, finding, impact, recommendation."""
        gen = InsightGenerator()
        insights = await gen.generate_insights(sample_df)
        for i in insights:
            assert i.number > 0
            assert len(i.title) > 0
            assert i.dimension in DIMENSIONS
            assert len(i.finding) > 0
            assert len(i.impact) > 0
            assert len(i.recommendation) > 0

    @pytest.mark.asyncio
    async def test_insights_cover_all_dimensions(self, sample_df):
        """Each insight covers a different dimension."""
        gen = InsightGenerator()
        insights = await gen.generate_insights(sample_df)
        dims = {i.dimension for i in insights}
        assert dims == set(DIMENSIONS)

    @pytest.mark.asyncio
    async def test_empty_df_returns_empty(self):
        """Empty DataFrame returns no insights."""
        gen = InsightGenerator()
        insights = await gen.generate_insights(pd.DataFrame())
        assert len(insights) == 0


class TestInsightToHtml:
    def test_html_contains_fields(self):
        """Insight.to_html() includes all fields."""
        i = Insight(
            number=1, title="Test", dimension="Posicionamiento de Precios",
            finding="test finding", impact="test impact",
            recommendation="test rec",
        )
        html = i.to_html()
        assert "Insight #1" in html
        assert "test finding" in html
        assert "test impact" in html
        assert "test rec" in html


class TestExecutiveSummary:
    def test_template_summary_not_empty(self, sample_df):
        """Template-based executive summary is not empty."""
        gen = InsightGenerator()
        # Build minimal insights to avoid running full pipeline
        from src.analysis.insights import Insight

        insights = [
            Insight(1, "Test", "Posicionamiento de Precios", "f", "i", "r"),
        ]
        summary = gen._template_executive_summary(sample_df, insights)
        assert len(summary) > 20

    def test_template_summary_mentions_platforms(self, sample_df):
        """Template summary mentions number of platforms."""
        gen = InsightGenerator()
        from src.analysis.insights import Insight

        insights = [
            Insight(1, "Test", "Posicionamiento de Precios", "f", "i", "r"),
        ]
        summary = gen._template_executive_summary(sample_df, insights)
        assert "2 plataformas" in summary
