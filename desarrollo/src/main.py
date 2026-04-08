"""CLI entry point for the Competitive Intelligence scraping system."""

import argparse
import asyncio
import json
import sys

from src.config import Config
from src.models.schemas import Platform, StoreType
from src.scrapers.rappi import RappiScraper
from src.utils.logger import get_logger, setup_logger
from src.utils.ollama_client import OllamaClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="competitive-intelligence",
        description="Competitive Intelligence system for delivery platforms in Mexico",
    )

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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode: 1 platform, 1 address, verbose, headless=false",
    )
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
    # Load config
    config = Config.load()
    logger = get_logger()

    # Apply headless override
    scraper_config = config.get_scraper_config()
    if args.headless is not None:
        scraper_config.headless = args.headless

    # Filter platforms
    requested_platforms = [p.strip() for p in args.platforms.split(",")]
    platforms = []
    for p in requested_platforms:
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

    # Get product names for restaurant store group
    store_groups = config.get_store_groups()
    restaurant_group = next(
        (sg for sg in store_groups if sg.store_type == StoreType.RESTAURANT),
        None,
    )
    product_names = (
        [p.canonical_name for p in restaurant_group.products]
        if restaurant_group
        else ["Big Mac"]
    )
    store_name = restaurant_group.store_name if restaurant_group else "McDonald's"

    logger.info(
        f"Starting scrape: {len(platforms)} platform(s), "
        f"{len(addresses)} address(es), "
        f"{len(product_names)} product(s)"
    )

    # Check Ollama availability
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

    # Run scrapers
    all_results = []

    for platform in platforms:
        if platform == Platform.RAPPI:
            scraper = RappiScraper(scraper_config)
        else:
            logger.warning(
                f"{platform.value} not implemented in MVP 0, skipping"
            )
            continue

        try:
            await scraper.setup()

            for addr in addresses:
                result = await scraper.scrape_address(
                    address=addr,
                    store_type=StoreType.RESTAURANT,
                    store_name=store_name,
                    product_names=product_names,
                )
                all_results.append(result)

                # Print result summary
                if result.success:
                    logger.info(
                        f"[bold green]SUCCESS[/bold green] "
                        f"{result.platform.value} | {addr.label} | "
                        f"{len(result.items)} items | "
                        f"layer={result.scrape_layer.value}",
                    )
                else:
                    logger.warning(
                        f"FAILED {result.platform.value} | {addr.label} | "
                        f"{result.error_message}"
                    )

                if len(addresses) > 1:
                    await scraper.rate_limit_delay()

        finally:
            await scraper.teardown()

    # Print summary
    success_count = sum(1 for r in all_results if r.success)
    total = len(all_results)
    logger.info(f"Scraping complete: {success_count}/{total} successful")

    # Print results as JSON
    if all_results:
        print("\n--- Results JSON ---")
        for r in all_results:
            print(
                json.dumps(
                    r.model_dump(mode="json"),
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )
            )

    return 0 if success_count > 0 else 3


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    apply_debug_overrides(args)

    # Setup logger
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logger(level=log_level)

    exit_code = asyncio.run(run(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
