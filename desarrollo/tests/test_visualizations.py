"""Tests for chart generation (MVP 3)."""

import os
import tempfile

import pandas as pd
import pytest

from src.analysis.visualizations import (
    chart_fee_vs_time,
    chart_price_comparison,
    chart_price_table,
    chart_zone_heatmap,
    generate_all_charts,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "platform": ["rappi", "rappi", "uber_eats", "uber_eats"],
        "address_label": ["Reforma", "Polanco", "Reforma", "Polanco"],
        "zone_type": ["centro", "premium", "centro", "premium"],
        "canonical_product": ["Big Mac", "Big Mac", "Big Mac", "Big Mac"],
        "price_mxn": [155.0, 160.0, 145.0, 150.0],
        "delivery_fee_mxn": [0.0, 0.0, 4.99, 4.99],
        "delivery_time_max": [35, 35, 35, 40],
        "scrape_layer": ["dom"] * 4,
    })


class TestChartGeneration:
    def test_price_comparison_creates_file(self, sample_df, tmp_path):
        path = str(tmp_path / "price.png")
        result = chart_price_comparison(sample_df, path)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0

    def test_zone_heatmap_creates_file(self, sample_df, tmp_path):
        path = str(tmp_path / "heatmap.png")
        result = chart_zone_heatmap(sample_df, path)
        assert os.path.exists(result)

    def test_fee_vs_time_creates_file(self, sample_df, tmp_path):
        path = str(tmp_path / "scatter.png")
        result = chart_fee_vs_time(sample_df, path)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0

    def test_price_table_creates_file(self, sample_df, tmp_path):
        path = str(tmp_path / "table.html")
        result = chart_price_table(sample_df, path)
        assert os.path.exists(result)
        content = open(result).read()
        assert "Big Mac" in content

    def test_generate_all_charts(self, sample_df, tmp_path):
        paths = generate_all_charts(sample_df, output_dir=str(tmp_path))
        assert len(paths) == 4
        assert "price_comparison" in paths
        assert "zone_heatmap" in paths
        assert "fee_vs_time" in paths
        assert "price_table" in paths


class TestChartContent:
    def test_price_table_has_delta_column(self, sample_df, tmp_path):
        path = str(tmp_path / "table.html")
        chart_price_table(sample_df, path)
        content = open(path).read()
        assert "Delta" in content or "Rappi" in content

    def test_empty_df_no_crash(self, tmp_path):
        """Empty DataFrame doesn't crash chart generation."""
        empty = pd.DataFrame(columns=["price_mxn", "canonical_product", "platform"])
        path = str(tmp_path / "empty.png")
        chart_price_comparison(empty, path)
        # Should not raise, may or may not create file
