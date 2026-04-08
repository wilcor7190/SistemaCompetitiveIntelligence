"""Run summary: structured metrics for post-mortem analysis."""

import json
import time
from pathlib import Path

from src.models.schemas import ScrapingRun
from src.utils.logger import get_logger


def generate_run_summary(run: ScrapingRun) -> dict:
    """Generate a structured summary of a scraping run.

    Returns a dict with metrics, success rates, layer distribution,
    failures by platform, timing data, and per-address details.
    """
    summary = {
        "run_id": run.run_id,
        "start_time": run.start_time.isoformat(),
        "end_time": run.end_time.isoformat() if run.end_time else None,
        "duration_seconds": (
            (run.end_time - run.start_time).total_seconds()
            if run.end_time
            else None
        ),
        "platforms": [p.value for p in run.platforms],
        "addresses_count": run.addresses_count,
        "products_target": run.products_target,
        "totals": {
            "results_total": len(run.results),
            "results_successful": sum(1 for r in run.results if r.success),
            "results_failed": sum(1 for r in run.results if not r.success),
            "success_rate": round(run.success_rate, 3),
        },
        "layer_distribution": run.layer_distribution,
        "by_platform": {},
        "failures": [],
        "performance": {
            "avg_scrape_duration_seconds": None,
            "max_scrape_duration_seconds": None,
            "min_scrape_duration_seconds": None,
        },
    }

    # Per-platform breakdown
    for platform in run.platforms:
        platform_results = [r for r in run.results if r.platform == platform]
        platform_success = [r for r in platform_results if r.success]
        platform_total_items = sum(len(r.items) for r in platform_success)

        summary["by_platform"][platform.value] = {
            "results_total": len(platform_results),
            "results_successful": len(platform_success),
            "items_extracted": platform_total_items,
            "success_rate": (
                round(len(platform_success) / len(platform_results), 3)
                if platform_results
                else 0.0
            ),
            "layers_used": _count_layers(platform_results),
        }

    # Collect failures with reasons
    for r in run.results:
        if not r.success:
            summary["failures"].append(
                {
                    "platform": r.platform.value,
                    "address": r.address.label,
                    "store_type": r.store_type.value,
                    "store_name": r.store_name,
                    "error_message": r.error_message,
                    "screenshot": r.screenshot_path,
                    "duration_seconds": r.scrape_duration_seconds,
                }
            )

    # Performance metrics
    durations = [
        r.scrape_duration_seconds
        for r in run.results
        if r.scrape_duration_seconds is not None
    ]
    if durations:
        summary["performance"]["avg_scrape_duration_seconds"] = round(
            sum(durations) / len(durations), 2
        )
        summary["performance"]["max_scrape_duration_seconds"] = round(
            max(durations), 2
        )
        summary["performance"]["min_scrape_duration_seconds"] = round(
            min(durations), 2
        )

    return summary


def _count_layers(results: list) -> dict[str, int]:
    """Count how many results used each scrape layer."""
    counts: dict[str, int] = {}
    for r in results:
        if r.success:
            layer = r.scrape_layer.value
            counts[layer] = counts.get(layer, 0) + 1
    return counts


def save_run_summary(
    run: ScrapingRun,
    output_dir: str = "logs",
) -> str:
    """Save the run summary as JSON for post-mortem analysis.

    Returns the path to the saved file.
    """
    logger = get_logger()
    summary = generate_run_summary(run)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = f"run_summary_{ts}_{run.run_id}.json"
    filepath = output_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"[summary] Run summary saved: {filepath}")
    return str(filepath)


def print_run_summary(run: ScrapingRun) -> None:
    """Print a human-readable summary to the console."""
    logger = get_logger()
    summary = generate_run_summary(run)

    logger.info("=" * 60)
    logger.info(f"RUN SUMMARY — {summary['run_id']}")
    logger.info("=" * 60)

    if summary["duration_seconds"]:
        logger.info(f"Duration: {summary['duration_seconds']:.1f}s")

    totals = summary["totals"]
    logger.info(
        f"Results: {totals['results_successful']}/{totals['results_total']} "
        f"successful ({totals['success_rate']:.0%})"
    )

    if summary["layer_distribution"]:
        layers_str = ", ".join(
            f"{k}: {v}" for k, v in summary["layer_distribution"].items()
        )
        logger.info(f"Layers used: {layers_str}")

    logger.info("By platform:")
    for platform, stats in summary["by_platform"].items():
        logger.info(
            f"  {platform}: {stats['results_successful']}/{stats['results_total']} "
            f"({stats['success_rate']:.0%}), {stats['items_extracted']} items"
        )

    if summary["failures"]:
        logger.warning(f"Failures: {len(summary['failures'])}")
        for f in summary["failures"][:5]:
            logger.warning(
                f"  [{f['platform']}] {f['address']} {f['store_type']}: "
                f"{f['error_message']}"
            )
        if len(summary["failures"]) > 5:
            logger.warning(f"  ... and {len(summary['failures']) - 5} more")

    perf = summary["performance"]
    if perf["avg_scrape_duration_seconds"]:
        logger.info(
            f"Performance: avg {perf['avg_scrape_duration_seconds']}s | "
            f"min {perf['min_scrape_duration_seconds']}s | "
            f"max {perf['max_scrape_duration_seconds']}s"
        )

    logger.info("=" * 60)
