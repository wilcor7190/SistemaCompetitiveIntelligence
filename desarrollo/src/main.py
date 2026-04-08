"""CLI entry point for the Competitive Intelligence scraping system."""

import argparse
import asyncio
import json
import shutil
import sys
import time
from pathlib import Path

from src.config import Config
from src.models.schemas import Platform, StoreType
from src.scrapers.orchestrator import ScrapingOrchestrator
from src.utils.logger import get_logger, setup_logger
from src.utils.ollama_client import OllamaClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="competitive-intelligence",
        description="Competitive Intelligence system for delivery platforms in Mexico",
    )

    # Scraping options
    parser.add_argument(
        "--platforms",
        type=str,
        default="rappi,uber_eats,didi_food",
        help="Platforms to scrape (comma-separated)",
    )
    parser.add_argument(
        "--max-addresses",
        type=int,
        default=0,
        help="Limit to N addresses (0 = all)",
    )

    # Mode shortcuts
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode: 1 platform, 1 address, verbose, headless=false",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show execution plan without scraping",
    )

    # Browser options
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Run browser headless (default: from settings)",
    )
    parser.add_argument(
        "--screenshots",
        action="store_true",
        help="Capture screenshots on every extraction",
    )

    # Report options
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Skip scraping, generate report from existing data",
    )
    parser.add_argument(
        "--report-data",
        type=str,
        default="data/merged/comparison.csv",
        help="CSV to use with --report-only",
    )

    # Backup options
    parser.add_argument(
        "--save-backup",
        action="store_true",
        help="Save a copy of raw data to data/backup/",
    )
    parser.add_argument(
        "--use-backup",
        action="store_true",
        help="Use pre-scraped data from data/backup/ instead of scraping",
    )

    return parser


def apply_debug_overrides(args: argparse.Namespace) -> None:
    """Override settings for quick PoC testing."""
    if args.debug:
        args.platforms = "rappi"
        args.max_addresses = 1
        if args.headless is None:
            args.headless = False


async def run(args: argparse.Namespace) -> int:
    """Main async execution flow."""
    config = Config.load()
    logger = get_logger()

    # Apply headless override
    scraper_config = config.get_scraper_config()
    if args.headless is not None:
        scraper_config.headless = args.headless

    # Filter platforms
    requested = [p.strip() for p in args.platforms.split(",")]
    platforms = []
    for p in requested:
        try:
            platforms.append(Platform(p))
        except ValueError:
            logger.warning(f"Unknown platform: {p}, skipping")

    if not platforms:
        logger.error("No valid platforms specified")
        return 1

    # Filter addresses
    addresses = config.get_addresses()
    if args.max_addresses > 0:
        addresses = addresses[: args.max_addresses]

    # Filter store groups — for MVP 1, only restaurant + convenience
    store_groups = config.get_store_groups()
    active_groups = [
        sg for sg in store_groups
        if sg.store_type in (StoreType.RESTAURANT, StoreType.CONVENIENCE)
    ]

    # Dry run
    if args.dry_run:
        products = [p.canonical_name for sg in active_groups for p in sg.products]
        logger.info(f"Plan: {len(platforms)} platform(s)")
        logger.info(f"  Addresses: {len(addresses)}")
        logger.info(f"  Store groups: {len(active_groups)}")
        logger.info(f"  Products: {products}")
        logger.info(
            f"  Estimated data points: "
            f"~{len(platforms) * len(addresses) * len(products)}"
        )
        return 0

    # Check Ollama
    ollama = OllamaClient(
        base_url=config.get_ollama_config().base_url,
        timeout=config.get_ollama_config().timeout,
    )
    if await ollama.is_available():
        models = await ollama.list_models()
        logger.info(f"Ollama available. Models: {', '.join(models[:5])}")
    else:
        logger.warning(
            "Ollama not available. Layers 2-fallback and 3 disabled."
        )

    paths = config.get_paths()
    csv_path = None

    # --report-only: skip scraping, use existing CSV
    if args.report_only:
        csv_path = args.report_data
        if not Path(csv_path).exists():
            logger.error(f"CSV not found: {csv_path}")
            return 1
        logger.info(f"Report-only mode: using {csv_path}")
    else:
        # Run orchestrator
        orchestrator = ScrapingOrchestrator(config)

        run_result = await orchestrator.run_all(
            platforms=platforms,
            addresses=addresses,
            store_groups=active_groups,
        )

        # Normalize and merge to CSV
        if run_result.results:
            csv_path = await orchestrator.normalize_and_merge(
                run_result, output_dir=paths["merged_data"]
            )
            logger.info(f"CSV saved: {csv_path}")

            # Save backup if requested
            if args.save_backup:
                backup_dir = Path("data/backup")
                backup_dir.mkdir(parents=True, exist_ok=True)
                ts = time.strftime("%Y%m%d_%H%M%S")

                raw_dir = Path(paths["raw_data"])
                for f in raw_dir.glob("*.json"):
                    shutil.copy2(f, backup_dir / f"backup_{ts}_{f.name}")
                shutil.copy2(csv_path, backup_dir / f"comparison_backup_{ts}.csv")
                logger.info(f"Backup saved to {backup_dir}")

        # Print scraping summary
        success = sum(1 for r in run_result.results if r.success)
        total = len(run_result.results)
        logger.info(
            f"Scraping done: {success}/{total} successful "
            f"({run_result.success_rate:.0%}) | Layers: {run_result.layer_distribution}"
        )

    # Generate insights and report
    if csv_path and Path(csv_path).exists():
        await _generate_report(csv_path, paths, logger)

    return 0


async def _generate_report(csv_path: str, paths: dict, logger) -> None:
    """Generate charts, insights, and HTML report from CSV."""
    import pandas as pd

    from src.analysis.insights import InsightGenerator
    from src.analysis.report_generator import ReportGenerator
    from src.analysis.visualizations import generate_all_charts

    df = pd.read_csv(csv_path)
    if df.empty:
        logger.warning("CSV is empty, skipping report generation")
        return

    logger.info(f"Generating report from {len(df)} rows...")

    # Charts
    charts_dir = paths.get("charts", "reports/charts")
    chart_paths = generate_all_charts(df, output_dir=charts_dir)
    logger.info(f"Charts generated: {list(chart_paths.keys())}")

    # Insights
    generator = InsightGenerator()
    insights = await generator.generate_insights(df)
    executive_summary = generator.generate_executive_summary(df, insights)
    logger.info(f"Insights generated: {len(insights)}")

    # HTML Report
    report = ReportGenerator()
    report_path = paths.get("reports", "reports") + "/insights.html"
    report.generate(
        df=df,
        insights=insights,
        executive_summary=executive_summary,
        chart_paths=chart_paths,
        output_path=report_path,
    )
    logger.info(f"Report: {report_path}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    apply_debug_overrides(args)

    log_level = "DEBUG" if args.debug else "INFO"
    setup_logger(level=log_level)

    exit_code = asyncio.run(run(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
