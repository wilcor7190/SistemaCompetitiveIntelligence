"""ReportGenerator: creates a self-contained HTML report."""

import base64
import time
from pathlib import Path

import pandas as pd

from src.analysis.insights import Insight
from src.utils.logger import get_logger


class ReportGenerator:
    """Generates a self-contained HTML report with embedded images."""

    def __init__(self):
        self.logger = get_logger()

    def generate(
        self,
        df: pd.DataFrame,
        insights: list[Insight],
        executive_summary: str,
        chart_paths: dict[str, str],
        output_path: str = "reports/insights.html",
    ) -> str:
        """Generate the HTML report."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Embed images as base64
        charts_html = self._embed_charts(chart_paths)

        # Build scraping summary table
        summary_html = self._build_summary_table(df)

        # Build insights HTML
        insights_html = "\n".join(i.to_html() for i in insights)

        # Build price table
        price_table_path = chart_paths.get("price_table", "")
        price_table_html = ""
        if price_table_path and Path(price_table_path).exists():
            price_table_html = Path(price_table_path).read_text(encoding="utf-8")

        # Build full HTML
        html = self._build_html(
            executive_summary=executive_summary,
            summary_table=summary_html,
            charts=charts_html,
            insights=insights_html,
            price_table=price_table_html,
            n_datapoints=len(df),
        )

        Path(output_path).write_text(html, encoding="utf-8")
        self.logger.info(f"[report] HTML report saved: {output_path}")
        return output_path

    def _embed_charts(self, chart_paths: dict[str, str]) -> dict[str, str]:
        """Convert PNG files to base64 data URIs."""
        embedded = {}
        for name, path in chart_paths.items():
            if path and Path(path).exists() and path.endswith(".png"):
                data = Path(path).read_bytes()
                b64 = base64.b64encode(data).decode("utf-8")
                embedded[name] = f"data:image/png;base64,{b64}"
        return embedded

    def _build_summary_table(self, df: pd.DataFrame) -> str:
        """Build HTML table with scraping coverage summary."""
        if df.empty:
            return "<p>No hay datos de scraping.</p>"

        rows = []
        for platform in df.platform.unique():
            pdata = df[df.platform == platform]
            n_dirs = pdata.address_label.nunique()
            n_items = len(pdata)
            layers = (
                pdata.scrape_layer.value_counts().to_dict()
                if "scrape_layer" in pdata.columns
                else {}
            )
            layers_str = ", ".join(f"{k}: {v}" for k, v in layers.items())
            rows.append(
                f"<tr><td>{platform}</td><td>{n_dirs}</td>"
                f"<td>{n_items}</td><td>{layers_str}</td></tr>"
            )

        return f"""
        <table class="summary-table">
            <thead>
                <tr><th>Plataforma</th><th>Direcciones</th><th>Data Points</th><th>Capas</th></tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
        """

    def _build_html(
        self,
        executive_summary: str,
        summary_table: str,
        charts: dict[str, str],
        insights: str,
        price_table: str,
        n_datapoints: int,
    ) -> str:
        """Build the complete HTML document."""
        date = time.strftime("%Y-%m-%d %H:%M")

        price_chart = charts.get("price_comparison", "")
        heatmap_chart = charts.get("zone_heatmap", "")
        scatter_chart = charts.get("fee_vs_time", "")

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Competitive Intelligence Report - CDMX</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
        .container {{ max-width: 960px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #FF6B35, #FF8F65); color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px; text-align: center; }}
        .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
        .header .subtitle {{ font-size: 16px; opacity: 0.9; }}
        .header .meta {{ font-size: 13px; opacity: 0.7; margin-top: 12px; }}
        .section {{ background: white; border-radius: 10px; padding: 30px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .section h2 {{ font-size: 20px; color: #FF6B35; margin-bottom: 16px; border-bottom: 2px solid #FF6B35; padding-bottom: 8px; }}
        .executive-summary {{ font-size: 16px; background: #FFF8F5; padding: 20px; border-left: 4px solid #FF6B35; border-radius: 4px; }}
        .summary-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        .summary-table th {{ background: #FF6B35; color: white; padding: 10px 14px; text-align: left; }}
        .summary-table td {{ padding: 10px 14px; border-bottom: 1px solid #eee; }}
        .summary-table tr:hover {{ background: #FFF8F5; }}
        .chart-container {{ text-align: center; margin: 20px 0; }}
        .chart-container img {{ max-width: 100%; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }}
        .chart-container .caption {{ font-size: 13px; color: #666; margin-top: 8px; font-style: italic; }}
        .insight {{ background: #FAFAFA; border-radius: 8px; padding: 20px; margin: 16px 0; border-left: 4px solid #FF6B35; }}
        .insight h3 {{ color: #FF6B35; margin-bottom: 10px; }}
        .insight p {{ margin: 6px 0; }}
        .price-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        .price-table th, .price-table td {{ padding: 10px; border: 1px solid #ddd; text-align: right; }}
        .price-table th {{ background: #f0f0f0; text-align: left; }}
        .limitations {{ background: #FFF3E0; padding: 16px; border-radius: 8px; }}
        .limitations li {{ margin: 6px 0; }}
        .methodology {{ font-size: 14px; color: #666; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Competitive Intelligence Report</h1>
            <div class="subtitle">Delivery Platforms &mdash; CDMX, Abril 2026</div>
            <div class="meta">Generado: {date} | {n_datapoints} data points</div>
        </div>

        <div class="section">
            <h2>Resumen Ejecutivo</h2>
            <div class="executive-summary">{executive_summary}</div>
        </div>

        <div class="section">
            <h2>Datos del Scraping</h2>
            {summary_table}
        </div>

        <div class="section">
            <h2>Comparativa de Precios</h2>
            {"<div class='chart-container'><img src='" + price_chart + "' alt='Price Comparison'><div class='caption'>Precios de productos de referencia en McDonald's por plataforma</div></div>" if price_chart else "<p>Chart no disponible.</p>"}
        </div>

        <div class="section">
            <h2>Top 5 Insights</h2>
            {insights}
        </div>

        <div class="section">
            <h2>Variabilidad por Zona</h2>
            {"<div class='chart-container'><img src='" + heatmap_chart + "' alt='Zone Heatmap'><div class='caption'>Diferencia porcentual de precios Rappi vs competencia por zona y producto</div></div>" if heatmap_chart else "<p>Chart no disponible (requiere datos de multiples plataformas).</p>"}
        </div>

        <div class="section">
            <h2>Fee vs Tiempo de Entrega</h2>
            {"<div class='chart-container'><img src='" + scatter_chart + "' alt='Fee vs Time'><div class='caption'>Relacion entre costo de envio y tiempo de entrega por plataforma</div></div>" if scatter_chart else "<p>Chart no disponible.</p>"}
        </div>

        {"<div class='section'><h2>Tabla de Precios</h2>" + price_table + "</div>" if price_table else ""}

        <div class="section">
            <h2>Limitaciones y Next Steps</h2>
            <div class="limitations">
                <ul>
                    <li>Service fee no accesible sin simular compra (ADR-003)</li>
                    <li>DiDi Food con cobertura parcial (SPA sin SSR)</li>
                    <li>Datos de un punto en el tiempo (no tendencia temporal)</li>
                    <li>Next: scheduler diario, mas ciudades, dashboard interactivo</li>
                </ul>
            </div>
        </div>

        <div class="section">
            <h2>Metodologia</h2>
            <div class="methodology">
                <p>Sistema de 3 capas de recoleccion (API Interception &rarr; DOM Parsing &rarr; Vision AI).
                25 direcciones en 5 zonas de CDMX. 6 productos de referencia (McDonald's + retail).
                Modelos Ollama locales: qwen3-vl (OCR), qwen3.5 (parsing/insights), nomic-embed-text (matching).</p>
            </div>
        </div>

        <div class="footer">
            Generated by Competitive Intelligence System v0.3.0 &mdash; AI-assisted insights
        </div>
    </div>
</body>
</html>"""
