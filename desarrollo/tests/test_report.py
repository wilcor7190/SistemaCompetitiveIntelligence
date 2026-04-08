"""Tests for HTML report generation (MVP 3)."""

import os

import pandas as pd
import pytest

from src.analysis.insights import Insight, InsightGenerator
from src.analysis.report_generator import ReportGenerator
from src.analysis.visualizations import generate_all_charts


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "platform": ["rappi", "uber_eats"],
        "address_label": ["Reforma", "Reforma"],
        "zone_type": ["centro", "centro"],
        "canonical_product": ["Big Mac", "Big Mac"],
        "original_product_name": ["Big Mac Tocino", "Big Mac"],
        "price_mxn": [155.0, 145.0],
        "delivery_fee_mxn": [0.0, 4.99],
        "delivery_time_min": [35, 25],
        "delivery_time_max": [35, 35],
        "promotions": ["Envio Gratis", ""],
        "rating": [4.1, 4.5],
        "scrape_layer": ["dom", "dom"],
        "store_type": ["restaurant", "restaurant"],
        "store_name": ["McDonald's", "McDonald's"],
    })


@pytest.fixture
def sample_insights():
    return [
        Insight(i, f"Title {i}", dim, "finding", "impact", "recommendation")
        for i, dim in enumerate(
            [
                "Posicionamiento de Precios",
                "Ventaja Operacional",
                "Estructura de Fees",
                "Estrategia Promocional",
                "Variabilidad Geografica",
            ],
            1,
        )
    ]


class TestHtmlReport:
    def test_html_report_created(self, sample_df, sample_insights, tmp_path):
        """Report generates an HTML file."""
        charts = generate_all_charts(sample_df, output_dir=str(tmp_path / "charts"))
        report = ReportGenerator()
        path = str(tmp_path / "report.html")
        result = report.generate(
            df=sample_df,
            insights=sample_insights,
            executive_summary="Test summary.",
            chart_paths=charts,
            output_path=path,
        )
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0

    def test_html_contains_sections(self, sample_df, sample_insights, tmp_path):
        """Report HTML contains all expected sections."""
        charts = generate_all_charts(sample_df, output_dir=str(tmp_path / "charts"))
        report = ReportGenerator()
        path = str(tmp_path / "report.html")
        report.generate(
            df=sample_df,
            insights=sample_insights,
            executive_summary="Test summary.",
            chart_paths=charts,
            output_path=path,
        )
        html = open(path, encoding="utf-8").read()

        assert "Competitive Intelligence Report" in html
        assert "Resumen Ejecutivo" in html
        assert "Test summary." in html
        assert "Cobertura del Scraping" in html
        assert "Comparativa de Precios" in html
        assert "Top 5 Insights" in html
        assert "#1" in html  # insight number rendered as #1
        assert "Limitaciones" in html
        assert "Metodologia" in html

    def test_html_self_contained(self, sample_df, sample_insights, tmp_path):
        """Report has images embedded as base64 (no external refs)."""
        charts = generate_all_charts(sample_df, output_dir=str(tmp_path / "charts"))
        report = ReportGenerator()
        path = str(tmp_path / "report.html")
        report.generate(
            df=sample_df,
            insights=sample_insights,
            executive_summary="Test summary.",
            chart_paths=charts,
            output_path=path,
        )
        html = open(path, encoding="utf-8").read()

        # Charts should be embedded as base64
        assert "data:image/png;base64," in html
        # No external image references
        assert 'src="reports/' not in html
        assert 'src="charts/' not in html
