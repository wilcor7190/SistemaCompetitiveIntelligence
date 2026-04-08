"""InsightGenerator: generate 5 actionable insights from scraped data.

Uses Claude API (Opus 4.6) for narrative executive summary if ANTHROPIC_API_KEY
is set. Always generates 5 stats-based insights (one per brief dimension).
"""

import pandas as pd

from src.utils.claude_client import ClaudeClient
from src.utils.logger import get_logger

# 5 dimensions from the brief
DIMENSIONS = [
    "Posicionamiento de Precios",
    "Ventaja Operacional",
    "Estructura de Fees",
    "Estrategia Promocional",
    "Variabilidad Geografica",
]


class Insight:
    """A single actionable insight."""

    def __init__(
        self,
        number: int,
        title: str,
        dimension: str,
        finding: str,
        impact: str,
        recommendation: str,
    ):
        self.number = number
        self.title = title
        self.dimension = dimension
        self.finding = finding
        self.impact = impact
        self.recommendation = recommendation

    def to_html(self) -> str:
        return f"""
        <div class="insight">
            <h3>Insight #{self.number}: {self.title}</h3>
            <p><strong>Dimension:</strong> {self.dimension}</p>
            <p><strong>Finding:</strong> {self.finding}</p>
            <p><strong>Impacto:</strong> {self.impact}</p>
            <p><strong>Recomendacion:</strong> {self.recommendation}</p>
        </div>
        """


class InsightGenerator:
    """Generates 5 insights from comparison data."""

    def __init__(
        self,
        claude_client: ClaudeClient | None = None,
    ):
        self.claude = claude_client or ClaudeClient()
        self.logger = get_logger()

    async def generate_insights(self, df: pd.DataFrame) -> list[Insight]:
        """Generate 5 insights, one per dimension.

        Always uses stats-based generation (reliable, deterministic).
        Claude is used only for the executive summary (if API key set).
        """
        if df.empty:
            self.logger.warning("[insights] Empty DataFrame, no insights")
            return []

        return self._generate_stats_insights(df)

    def _generate_stats_insights(self, df: pd.DataFrame) -> list[Insight]:
        """Generate insights using pandas statistics (no LLM)."""
        insights: list[Insight] = []

        # --- Insight 1: Posicionamiento de Precios ---
        insights.append(self._insight_pricing(df))

        # --- Insight 2: Ventaja Operacional ---
        insights.append(self._insight_operational(df))

        # --- Insight 3: Estructura de Fees ---
        insights.append(self._insight_fees(df))

        # --- Insight 4: Estrategia Promocional ---
        insights.append(self._insight_promotions(df))

        # --- Insight 5: Variabilidad Geografica ---
        insights.append(self._insight_geographic(df))

        self.logger.info(f"[insights] Generated {len(insights)} stats-based insights")
        return insights

    def _insight_pricing(self, df: pd.DataFrame) -> Insight:
        """Insight 1: Price positioning."""
        data = df.dropna(subset=["price_mxn"])
        if data.empty:
            return self._empty_insight(1, "Posicionamiento de Precios")

        avg_by_platform = data.groupby("platform").price_mxn.mean().round(2)
        platforms = avg_by_platform.to_dict()

        cheapest = avg_by_platform.idxmin()
        most_expensive = avg_by_platform.idxmax()
        delta_pct = 0.0
        if len(avg_by_platform) >= 2:
            delta_pct = (
                (avg_by_platform.max() - avg_by_platform.min())
                / avg_by_platform.min()
                * 100
            )

        prices_str = ", ".join(f"{k}: ${v}" for k, v in platforms.items())

        return Insight(
            number=1,
            title=f"{most_expensive.replace('_', ' ').title()} es la plataforma mas cara",
            dimension="Posicionamiento de Precios",
            finding=f"Precio promedio por plataforma: {prices_str}. "
            f"Diferencia de {delta_pct:.1f}% entre la mas cara y la mas barata.",
            impact=f"{most_expensive.replace('_', ' ').title()} cobra en promedio "
            f"${avg_by_platform.max():.0f} vs ${avg_by_platform.min():.0f} de "
            f"{cheapest.replace('_', ' ').title()}, afectando competitividad en precio.",
            recommendation=f"Rappi deberia monitorear precios de {cheapest.replace('_', ' ').title()} "
            f"y ajustar su pricing para productos de alta rotacion.",
        )

    def _insight_operational(self, df: pd.DataFrame) -> Insight:
        """Insight 2: Operational advantage (delivery time)."""
        data = df.dropna(subset=["delivery_time_min"])
        if data.empty:
            return self._empty_insight(2, "Ventaja Operacional")

        avg_time = data.groupby("platform").delivery_time_min.mean().round(1)
        times_str = ", ".join(f"{k}: {v} min" for k, v in avg_time.to_dict().items())
        fastest = avg_time.idxmin()

        total_products = data.groupby("platform").canonical_product.count()
        coverage_str = ", ".join(
            f"{k}: {v} productos" for k, v in total_products.to_dict().items()
        )

        return Insight(
            number=2,
            title=f"{fastest.replace('_', ' ').title()} tiene los tiempos mas rapidos",
            dimension="Ventaja Operacional",
            finding=f"Tiempo promedio de entrega: {times_str}. "
            f"Cobertura de productos: {coverage_str}.",
            impact="Tiempos de entrega mas rapidos correlacionan con mayor retencion "
            "de usuarios y mayor frecuencia de pedido.",
            recommendation="Optimizar rutas y tiempos de preparacion en zonas donde "
            "la competencia tiene ventaja operacional.",
        )

    def _insight_fees(self, df: pd.DataFrame) -> Insight:
        """Insight 3: Fee structure."""
        data = df.dropna(subset=["delivery_fee_mxn"])
        if data.empty:
            return self._empty_insight(3, "Estructura de Fees")

        avg_fee = data.groupby("platform").delivery_fee_mxn.mean().round(2)
        fees_str = ", ".join(f"{k}: ${v}" for k, v in avg_fee.to_dict().items())

        free_delivery = data[data.delivery_fee_mxn == 0]
        free_pct = (len(free_delivery) / len(data) * 100) if len(data) > 0 else 0

        return Insight(
            number=3,
            title="Delivery fees como diferenciador competitivo",
            dimension="Estructura de Fees",
            finding=f"Fee promedio: {fees_str}. "
            f"{free_pct:.0f}% de las observaciones tienen envio gratis.",
            impact="El delivery fee afecta directamente la percepcion de precio total "
            "del usuario. Un fee de $0 puede compensar un precio de producto mas alto.",
            recommendation="Evaluar estrategia de envio gratis condicional "
            "(ej: gratis en pedidos >$149) para competir con plataformas de fee bajo.",
        )

    def _insight_promotions(self, df: pd.DataFrame) -> Insight:
        """Insight 4: Promotional strategy."""
        data = df.dropna(subset=["promotions"])
        promo_data = data[data.promotions.str.len() > 0]

        promo_count = len(promo_data)
        total = len(df)
        promo_pct = (promo_count / total * 100) if total > 0 else 0

        # Count by platform
        by_platform = (
            promo_data.groupby("platform").size().to_dict()
            if not promo_data.empty
            else {}
        )
        promos_str = (
            ", ".join(f"{k}: {v}" for k, v in by_platform.items()) or "sin datos"
        )

        return Insight(
            number=4,
            title="Promociones como herramienta de adquisicion",
            dimension="Estrategia Promocional",
            finding=f"{promo_pct:.0f}% de las observaciones tienen promociones activas. "
            f"Por plataforma: {promos_str}.",
            impact="Las promociones agresivas (envio gratis, descuentos) son el principal "
            "driver de nuevos usuarios en delivery. Rappi usa 'Envio Gratis' como ancla.",
            recommendation="Monitorear frecuencia y tipo de promociones de la competencia "
            "para responder con ofertas targetadas por zona y horario.",
        )

    def _insight_geographic(self, df: pd.DataFrame) -> Insight:
        """Insight 5: Geographic variability."""
        data = df.dropna(subset=["price_mxn", "zone_type"])
        if data.empty:
            return self._empty_insight(5, "Variabilidad Geografica")

        avg_by_zone = data.groupby("zone_type").price_mxn.mean().round(2)
        zones_str = ", ".join(f"{k}: ${v}" for k, v in avg_by_zone.to_dict().items())

        most_expensive_zone = avg_by_zone.idxmax()
        cheapest_zone = avg_by_zone.idxmin()
        delta = avg_by_zone.max() - avg_by_zone.min()

        return Insight(
            number=5,
            title=f"Zona {most_expensive_zone} tiene precios {delta:.0f} MXN mas altos",
            dimension="Variabilidad Geografica",
            finding=f"Precio promedio por zona: {zones_str}. "
            f"Diferencia de ${delta:.0f} MXN entre {most_expensive_zone} y {cheapest_zone}.",
            impact="La variabilidad de precios por zona indica oportunidades de pricing "
            "dinamico y segmentacion geografica.",
            recommendation=f"Implementar pricing diferenciado por zona. "
            f"En {cheapest_zone} mantener precios bajos para volumen, "
            f"en {most_expensive_zone} hay margen para premium.",
        )

    def _empty_insight(self, number: int, dimension: str) -> Insight:
        return Insight(
            number=number,
            title=f"Datos insuficientes para {dimension}",
            dimension=dimension,
            finding="No hay datos suficientes para generar este insight.",
            impact="Se requieren mas datos de scraping.",
            recommendation="Ejecutar scraping completo con mas direcciones.",
        )

    async def generate_executive_summary(
        self, df: pd.DataFrame, insights: list[Insight]
    ) -> str:
        """Generate a 1-paragraph executive summary.

        If Claude API is available, generates a polished narrative.
        Otherwise falls back to a deterministic template.
        """
        if not insights:
            return "No hay datos suficientes para generar un resumen ejecutivo."

        # Try Claude API first for better quality
        if self.claude.is_available():
            llm_summary = await self._claude_executive_summary(df, insights)
            if llm_summary:
                return llm_summary

        # Fallback: deterministic template
        return self._template_executive_summary(df, insights)

    def _template_executive_summary(
        self, df: pd.DataFrame, insights: list[Insight]
    ) -> str:
        """Deterministic 1-paragraph summary (no LLM)."""
        n_platforms = df.platform.nunique() if not df.empty else 0
        n_addresses = df.address_label.nunique() if not df.empty else 0
        n_products = df.canonical_product.nunique() if not df.empty else 0

        top_finding = insights[0].finding if insights else ""

        return (
            f"Analisis de {n_platforms} plataformas de delivery en {n_addresses} "
            f"direcciones de CDMX con {n_products} productos de referencia. "
            f"{top_finding} "
            f"Se identificaron oportunidades en pricing, fees y cobertura geografica "
            f"que pueden traducirse en ventajas competitivas para Rappi."
        )

    async def _claude_executive_summary(
        self, df: pd.DataFrame, insights: list[Insight]
    ) -> str | None:
        """Generate a narrative executive summary using Claude API."""
        n_platforms = df.platform.nunique() if not df.empty else 0
        n_addresses = df.address_label.nunique() if not df.empty else 0
        n_products = df.canonical_product.nunique() if not df.empty else 0

        # Build context: insights as bullets
        insights_text = "\n".join(
            f"- {i.dimension}: {i.finding}" for i in insights
        )

        system = (
            "Eres un analista senior de competitive intelligence para Rappi Mexico. "
            "Tu trabajo es escribir resumenes ejecutivos accionables para VPs de Strategy. "
            "Responde en espanol profesional, sin bullet points, solo texto corrido."
        )

        prompt = f"""Escribe UN parrafo de resumen ejecutivo (max 100 palabras) para un VP de Strategy de Rappi.

Contexto:
- Analisis de {n_platforms} plataformas de delivery en {n_addresses} direcciones de CDMX
- {n_products} productos de referencia comparados
- Datos reales scrapeados de las plataformas

Insights detectados:
{insights_text}

El parrafo debe:
1. Empezar con el hallazgo mas impactante (cuantificado)
2. Conectar 2-3 insights clave de forma narrativa
3. Terminar con la recomendacion mas urgente

Responde SOLO con el parrafo, sin titulos ni explicaciones."""

        self.logger.info("[insights] Generating executive summary with Claude API...")
        result = await self.claude.chat(prompt=prompt, system=system, max_tokens=500)
        if result:
            self.logger.info("[insights] Claude executive summary generated")
        return result
