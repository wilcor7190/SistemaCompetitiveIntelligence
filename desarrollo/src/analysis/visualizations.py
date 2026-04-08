"""Visualizations: 4 charts for the competitive intelligence report."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils.logger import get_logger

# Platform brand colors
PLATFORM_COLORS = {
    "rappi": "#FF6B35",
    "uber_eats": "#06C167",
    "didi_food": "#FC6B2D",
}

PLATFORM_LABELS = {
    "rappi": "Rappi",
    "uber_eats": "Uber Eats",
    "didi_food": "DiDi Food",
}


def _ensure_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def chart_price_comparison(df: pd.DataFrame, output_path: str) -> str:
    """Bar chart: average price per product grouped by platform."""
    logger = get_logger()
    _ensure_dir(output_path)

    # Filter to matched canonical products only
    products_with_data = df.dropna(subset=["price_mxn", "canonical_product"])
    if products_with_data.empty:
        logger.warning("[viz] No price data for comparison chart")
        return output_path

    pivot = products_with_data.pivot_table(
        values="price_mxn",
        index="canonical_product",
        columns="platform",
        aggfunc="mean",
    ).round(2)

    colors = [PLATFORM_COLORS.get(c, "#999") for c in pivot.columns]
    labels = [PLATFORM_LABELS.get(c, c) for c in pivot.columns]

    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(kind="bar", ax=ax, color=colors, width=0.7)

    ax.set_title("Precio Promedio por Producto y Plataforma (MXN)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Precio (MXN)")
    ax.set_xlabel("")
    ax.legend(labels, title="Plataforma")
    ax.tick_params(axis="x", rotation=30)

    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt="$%.0f", fontsize=8, padding=2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"[viz] Price comparison chart saved: {output_path}")
    return output_path


def chart_zone_heatmap(df: pd.DataFrame, output_path: str) -> str:
    """Heatmap: price delta Rappi vs competition by zone and product."""
    logger = get_logger()
    _ensure_dir(output_path)

    data = df.dropna(subset=["price_mxn", "zone_type", "canonical_product"])
    if data.empty or "rappi" not in data.platform.values:
        logger.warning("[viz] Insufficient data for heatmap")
        return output_path

    rappi = data[data.platform == "rappi"].groupby(
        ["zone_type", "canonical_product"]
    ).price_mxn.mean()
    others = data[data.platform != "rappi"].groupby(
        ["zone_type", "canonical_product"]
    ).price_mxn.mean()

    if others.empty:
        # Only Rappi data — show absolute prices instead of delta
        pivot = rappi.unstack()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)
        ax.set_title("Precio Promedio Rappi por Zona y Producto (MXN)")
    else:
        delta = ((rappi - others) / others * 100).unstack()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(delta, annot=True, fmt=".1f", cmap="RdYlGn_r", center=0, ax=ax)
        ax.set_title(
            "Delta de Precio Rappi vs Competencia (%)\n"
            "Rojo = Rappi mas caro | Verde = Rappi mas barato"
        )

    ax.set_ylabel("Zona")
    ax.set_xlabel("Producto")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"[viz] Zone heatmap saved: {output_path}")
    return output_path


def chart_fee_vs_time(df: pd.DataFrame, output_path: str) -> str:
    """Scatter: delivery fee (X) vs delivery time (Y), colored by platform."""
    logger = get_logger()
    _ensure_dir(output_path)

    data = df.dropna(subset=["delivery_fee_mxn", "delivery_time_max"])
    if data.empty:
        logger.warning("[viz] No fee/time data for scatter chart")
        return output_path

    fig, ax = plt.subplots(figsize=(10, 6))

    for platform, group in data.groupby("platform"):
        ax.scatter(
            group.delivery_fee_mxn,
            group.delivery_time_max,
            c=PLATFORM_COLORS.get(platform, "#999"),
            label=PLATFORM_LABELS.get(platform, platform),
            alpha=0.6,
            s=80,
            edgecolors="white",
            linewidths=0.5,
        )

    ax.set_xlabel("Delivery Fee (MXN)")
    ax.set_ylabel("Tiempo de Entrega (min)")
    ax.set_title("Delivery Fee vs Tiempo de Entrega por Plataforma", fontsize=14, fontweight="bold")
    ax.legend(title="Plataforma")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"[viz] Fee vs time scatter saved: {output_path}")
    return output_path


def chart_price_table(df: pd.DataFrame, output_path: str) -> str:
    """HTML table: product x platform pivot with delta column."""
    logger = get_logger()
    _ensure_dir(output_path)

    data = df.dropna(subset=["price_mxn", "canonical_product"])
    if data.empty:
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

    html = pivot.to_html(classes="price-table", border=0)
    Path(output_path).write_text(html, encoding="utf-8")

    logger.info(f"[viz] Price table saved: {output_path}")
    return output_path


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
        "zone_heatmap": chart_zone_heatmap(
            df, f"{output_dir}/zone_heatmap.png"
        ),
        "fee_vs_time": chart_fee_vs_time(
            df, f"{output_dir}/fee_vs_time.png"
        ),
        "price_table": chart_price_table(
            df, f"{output_dir}/price_table.html"
        ),
    }
    return paths
