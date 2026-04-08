"""Visualizations: 4 charts for the competitive intelligence report.

All charts filter to **matched canonical products only** (Big Mac, McNuggets,
Coca-Cola 600ml, etc.) to keep them readable. Raw scraped products without
a canonical match are excluded from the visualizations.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.utils.logger import get_logger

# =============================================================================
# Rappi brand colors (oficial)
# =============================================================================
RAPPI_ORANGE = "#FF6B35"
RAPPI_DARK = "#1A1A1A"
RAPPI_GRAY = "#666666"
RAPPI_LIGHT = "#F5F5F5"

PLATFORM_COLORS = {
    "rappi": RAPPI_ORANGE,
    "uber_eats": "#06C167",
    "didi_food": "#FC6B2D",
}

PLATFORM_LABELS = {
    "rappi": "Rappi",
    "uber_eats": "Uber Eats",
    "didi_food": "DiDi Food",
}

# =============================================================================
# Canonical product list (los unicos que aparecen en los charts)
# =============================================================================
CANONICAL_PRODUCTS = {
    "Big Mac",
    "McNuggets 10 pzas",
    "Combo Mediano",
    "Coca-Cola 600ml",
    "Agua Bonafont 1L",
    "Panales",
}


def _ensure_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _filter_canonical(df: pd.DataFrame) -> pd.DataFrame:
    """Filter DataFrame to only canonical (matched) products.

    This is critical: without filtering we get 70+ unique products in
    the charts (every variant from McTrio Mediano to Paquete Botanero),
    which makes them illegible. We only want the products that matched
    to our reference list.
    """
    if df.empty or "canonical_product" not in df.columns:
        return df
    return df[df["canonical_product"].isin(CANONICAL_PRODUCTS)].copy()


def _setup_chart_style() -> None:
    """Apply consistent styling for all charts."""
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.titlesize"] = 16
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.labelweight"] = "bold"
    plt.rcParams["xtick.labelsize"] = 11
    plt.rcParams["ytick.labelsize"] = 11
    plt.rcParams["legend.fontsize"] = 11
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.edgecolor"] = "#CCCCCC"


# =============================================================================
# Chart 1: Price Comparison (bar chart)
# =============================================================================


def chart_price_comparison(df: pd.DataFrame, output_path: str) -> str:
    """Bar chart: average price per CANONICAL product grouped by platform.

    Only shows products in the canonical list (Big Mac, McNuggets, etc.).
    Other scraped products are excluded for readability.
    """
    logger = get_logger()
    _ensure_dir(output_path)
    _setup_chart_style()

    data = _filter_canonical(df.dropna(subset=["price_mxn", "canonical_product"]))

    if data.empty:
        logger.warning("[viz] No canonical product data for price chart")
        _save_empty_chart(output_path, "Sin datos para mostrar")
        return output_path

    pivot = data.pivot_table(
        values="price_mxn",
        index="canonical_product",
        columns="platform",
        aggfunc="mean",
    ).round(2)

    # Sort by Rappi price (or first column) descending for visual hierarchy
    if "rappi" in pivot.columns:
        pivot = pivot.sort_values("rappi", ascending=True)
    elif len(pivot.columns) > 0:
        pivot = pivot.sort_values(pivot.columns[0], ascending=True)

    colors = [PLATFORM_COLORS.get(c, "#999") for c in pivot.columns]
    labels = [PLATFORM_LABELS.get(c, c) for c in pivot.columns]

    fig, ax = plt.subplots(figsize=(11, 6))

    pivot.plot(
        kind="barh",  # horizontal = mejor para nombres largos
        ax=ax,
        color=colors,
        width=0.7,
        edgecolor="white",
        linewidth=1.5,
    )

    ax.set_title(
        "Precio Promedio por Producto y Plataforma",
        fontsize=16,
        fontweight="bold",
        color=RAPPI_DARK,
        pad=20,
    )
    ax.set_xlabel("Precio (MXN)", color=RAPPI_GRAY)
    ax.set_ylabel("")

    # Legend at bottom for cleaner look
    ax.legend(
        labels,
        title="Plataforma",
        loc="lower right",
        frameon=True,
        edgecolor="#CCCCCC",
    )

    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="$%.0f",
            fontsize=10,
            padding=4,
            color=RAPPI_DARK,
            fontweight="bold",
        )

    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(
        output_path, dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none"
    )
    plt.close()

    logger.info(f"[viz] Price comparison chart saved: {output_path}")
    return output_path


# =============================================================================
# Chart 2: Zone Heatmap
# =============================================================================


def chart_zone_heatmap(df: pd.DataFrame, output_path: str) -> str:
    """Heatmap: average price by zone and CANONICAL product.

    Only canonical products to keep heatmap readable.
    """
    logger = get_logger()
    _ensure_dir(output_path)
    _setup_chart_style()

    data = _filter_canonical(
        df.dropna(subset=["price_mxn", "zone_type", "canonical_product"])
    )

    if data.empty:
        logger.warning("[viz] No canonical data for heatmap")
        _save_empty_chart(output_path, "Sin datos suficientes")
        return output_path

    rappi = (
        data[data.platform == "rappi"]
        .groupby(["zone_type", "canonical_product"])
        .price_mxn.mean()
    )
    others = (
        data[data.platform != "rappi"]
        .groupby(["zone_type", "canonical_product"])
        .price_mxn.mean()
    )

    fig, ax = plt.subplots(figsize=(11, 6))

    if others.empty:
        # Only Rappi data — show absolute prices
        pivot = rappi.unstack()
        if pivot.empty:
            _save_empty_chart(output_path, "Sin datos suficientes")
            return output_path

        sns.heatmap(
            pivot,
            annot=True,
            fmt="$.0f",
            cmap="YlOrRd",
            ax=ax,
            cbar_kws={"label": "Precio (MXN)"},
            linewidths=1,
            linecolor="white",
            annot_kws={"fontsize": 11, "fontweight": "bold"},
        )
        ax.set_title(
            "Precio Promedio Rappi por Zona y Producto (MXN)",
            fontsize=16,
            fontweight="bold",
            color=RAPPI_DARK,
            pad=20,
        )
    else:
        delta = ((rappi - others) / others * 100).unstack()
        if delta.empty:
            _save_empty_chart(output_path, "Sin datos suficientes")
            return output_path

        sns.heatmap(
            delta,
            annot=True,
            fmt=".1f",
            cmap="RdYlGn_r",
            center=0,
            ax=ax,
            cbar_kws={"label": "Delta % vs competencia"},
            linewidths=1,
            linecolor="white",
            annot_kws={"fontsize": 11, "fontweight": "bold"},
        )
        ax.set_title(
            "Delta de Precio Rappi vs Competencia (%)",
            fontsize=16,
            fontweight="bold",
            color=RAPPI_DARK,
            pad=20,
        )
        # Subtitle
        ax.text(
            0.5,
            1.02,
            "Verde = Rappi mas barato | Rojo = Rappi mas caro",
            ha="center",
            va="bottom",
            transform=ax.transAxes,
            fontsize=10,
            color=RAPPI_GRAY,
            style="italic",
        )

    ax.set_ylabel("Zona", color=RAPPI_GRAY, fontweight="bold")
    ax.set_xlabel("Producto", color=RAPPI_GRAY, fontweight="bold")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    plt.tight_layout()
    plt.savefig(
        output_path, dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none"
    )
    plt.close()

    logger.info(f"[viz] Zone heatmap saved: {output_path}")
    return output_path


# =============================================================================
# Chart 3: Fee vs Time Scatter
# =============================================================================


def chart_fee_vs_time(df: pd.DataFrame, output_path: str) -> str:
    """Scatter: delivery fee vs delivery time, colored by platform.

    Adds jitter to avoid overlap when many points have same fee/time.
    Always shows the legend even if only 1 platform.
    """
    logger = get_logger()
    _ensure_dir(output_path)
    _setup_chart_style()

    data = df.dropna(subset=["delivery_fee_mxn", "delivery_time_max"]).copy()

    if data.empty:
        logger.warning("[viz] No fee/time data for scatter chart")
        _save_empty_chart(output_path, "Sin datos de fees/tiempos")
        return output_path

    # Aggregate per (platform, address) to avoid duplicates
    data = (
        data.groupby(["platform", "address_label"], as_index=False)
        .agg(
            {
                "delivery_fee_mxn": "first",
                "delivery_time_max": "first",
                "delivery_time_min": "first",
                "zone_type": "first",
            }
        )
    )

    # Add jitter to avoid overlap when multiple points share fee/time
    np.random.seed(42)
    data["fee_jitter"] = data["delivery_fee_mxn"] + np.random.uniform(
        -0.5, 0.5, len(data)
    )
    data["time_jitter"] = data["delivery_time_max"] + np.random.uniform(
        -1.5, 1.5, len(data)
    )

    fig, ax = plt.subplots(figsize=(11, 6))

    for platform, group in data.groupby("platform"):
        ax.scatter(
            group.fee_jitter,
            group.time_jitter,
            c=PLATFORM_COLORS.get(platform, "#999"),
            label=PLATFORM_LABELS.get(platform, platform),
            alpha=0.75,
            s=180,
            edgecolors="white",
            linewidths=2,
            zorder=3,
        )

    ax.set_xlabel("Delivery Fee (MXN)", color=RAPPI_GRAY)
    ax.set_ylabel("Tiempo de Entrega (min)", color=RAPPI_GRAY)
    ax.set_title(
        "Delivery Fee vs Tiempo de Entrega",
        fontsize=16,
        fontweight="bold",
        color=RAPPI_DARK,
        pad=20,
    )
    ax.legend(title="Plataforma", loc="best", frameon=True, edgecolor="#CCCCCC")
    ax.grid(True, alpha=0.3, linestyle="--", zorder=1)
    ax.set_axisbelow(True)

    # Add subtle annotation if all fees are 0
    if data["delivery_fee_mxn"].max() == 0 and data["delivery_fee_mxn"].min() == 0:
        ax.text(
            0.5,
            0.95,
            "Todas las observaciones tienen envio gratis ($0)",
            ha="center",
            va="top",
            transform=ax.transAxes,
            fontsize=10,
            color=RAPPI_GRAY,
            style="italic",
            bbox={
                "boxstyle": "round,pad=0.5",
                "facecolor": "#FFF8F5",
                "edgecolor": RAPPI_ORANGE,
                "linewidth": 1,
            },
        )

    # Set sensible axis limits if data is sparse
    if len(data) < 5:
        x_range = data["delivery_fee_mxn"].max() - data["delivery_fee_mxn"].min()
        y_range = data["delivery_time_max"].max() - data["delivery_time_max"].min()
        x_pad = max(x_range * 0.5, 5)
        y_pad = max(y_range * 0.5, 5)
        ax.set_xlim(
            data["delivery_fee_mxn"].min() - x_pad,
            data["delivery_fee_mxn"].max() + x_pad,
        )
        ax.set_ylim(
            data["delivery_time_max"].min() - y_pad,
            data["delivery_time_max"].max() + y_pad,
        )

    plt.tight_layout()
    plt.savefig(
        output_path, dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none"
    )
    plt.close()

    logger.info(f"[viz] Fee vs time scatter saved: {output_path}")
    return output_path


# =============================================================================
# Chart 4: Price Table (HTML)
# =============================================================================


def chart_price_table(df: pd.DataFrame, output_path: str) -> str:
    """HTML table: CANONICAL product x platform pivot with delta column."""
    logger = get_logger()
    _ensure_dir(output_path)

    data = _filter_canonical(df.dropna(subset=["price_mxn", "canonical_product"]))

    if data.empty:
        Path(output_path).write_text(
            "<p>Sin datos para mostrar.</p>", encoding="utf-8"
        )
        return output_path

    pivot = data.pivot_table(
        values="price_mxn",
        index="canonical_product",
        columns="platform",
        aggfunc="mean",
    ).round(2)

    # Rename columns
    pivot.columns = [PLATFORM_LABELS.get(c, c) for c in pivot.columns]

    # Add delta column if Rappi exists
    if "Rappi" in pivot.columns:
        other_cols = [c for c in pivot.columns if c != "Rappi"]
        if other_cols:
            others_mean = pivot[other_cols].mean(axis=1)
            pivot["Delta vs Competencia (%)"] = (
                (pivot["Rappi"] - others_mean) / others_mean * 100
            ).round(1)

    # Format prices with $ symbol
    for col in pivot.columns:
        if "Delta" not in col:
            pivot[col] = pivot[col].apply(
                lambda v: f"${v:.0f}" if pd.notna(v) else "—"
            )
        else:
            pivot[col] = pivot[col].apply(
                lambda v: f"{v:+.1f}%" if pd.notna(v) else "—"
            )

    pivot.index.name = "Producto"

    html = pivot.to_html(classes="price-table", border=0, escape=False)
    Path(output_path).write_text(html, encoding="utf-8")

    logger.info(f"[viz] Price table saved: {output_path}")
    return output_path


# =============================================================================
# Helpers
# =============================================================================


def _save_empty_chart(output_path: str, message: str) -> None:
    """Save a placeholder chart when there's no data."""
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        transform=ax.transAxes,
        fontsize=14,
        color=RAPPI_GRAY,
        style="italic",
    )
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    plt.savefig(
        output_path, dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none"
    )
    plt.close()


def generate_all_charts(
    df: pd.DataFrame,
    output_dir: str = "reports/charts",
) -> dict[str, str]:
    """Generate all 4 charts and return paths."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    paths = {
        "price_comparison": chart_price_comparison(
            df, f"{output_dir}/price_comparison.png"
        ),
        "zone_heatmap": chart_zone_heatmap(df, f"{output_dir}/zone_heatmap.png"),
        "fee_vs_time": chart_fee_vs_time(df, f"{output_dir}/fee_vs_time.png"),
        "price_table": chart_price_table(df, f"{output_dir}/price_table.html"),
    }
    return paths
