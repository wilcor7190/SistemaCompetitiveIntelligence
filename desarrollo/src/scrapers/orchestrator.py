"""ScrapingOrchestrator: coordinates scraping across addresses and store groups."""

import json
import time
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path

from src.config import Config
from src.models.schemas import (
    Address,
    Platform,
    ScrapedResult,
    ScrapingRun,
    StoreGroup,
)
from src.processors.merger import DataMerger
from src.processors.normalizer import DataNormalizer
from src.processors.product_matcher import ProductMatcher
from src.processors.validator import DataValidator
from src.scrapers.base import BaseScraper
from src.scrapers.didi_food import DiDiFoodScraper
from src.scrapers.rappi import RappiScraper
from src.scrapers.uber_eats import UberEatsScraper
from src.utils.claude_client import ClaudeClient
from src.utils.logger import get_logger


class ScrapingOrchestrator:
    """Orchestrates scraping across platforms, addresses, and store groups."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
        self.scraper_config = config.get_scraper_config()
        self.claude = ClaudeClient()

    def _create_scraper(self, platform: Platform) -> BaseScraper | None:
        """Factory: create the right scraper for a platform."""
        if platform == Platform.RAPPI:
            return RappiScraper(self.scraper_config)
        if platform == Platform.UBER_EATS:
            return UberEatsScraper(self.scraper_config)
        if platform == Platform.DIDI_FOOD:
            return DiDiFoodScraper(self.scraper_config)
        self.logger.warning(f"{platform.value} not implemented, skipping")
        return None

    async def run_all(
        self,
        platforms: list[Platform] | None = None,
        addresses: list[Address] | None = None,
        store_groups: list[StoreGroup] | None = None,
        save_raw: bool = True,
    ) -> ScrapingRun:
        """Run scraping for all platforms × addresses × store groups."""
        platforms = platforms or self.config.get_platforms()
        addresses = addresses or self.config.get_addresses()
        store_groups = store_groups or self.config.get_store_groups()

        run = ScrapingRun(
            run_id=str(uuid.uuid4())[:8],
            start_time=datetime.now(),
            platforms=platforms,
            addresses_count=len(addresses),
            products_target=[
                p.canonical_name for sg in store_groups for p in sg.products
            ],
        )

        self.logger.info(
            f"Starting run {run.run_id}: "
            f"{len(platforms)} platform(s) × {len(addresses)} address(es) × "
            f"{len(store_groups)} store group(s)"
        )

        for platform in platforms:
            results = await self.run_platform(platform, addresses, store_groups)
            run.results.extend(results)

            if save_raw:
                self._save_raw_results(platform, results, run.run_id)

        run.end_time = datetime.now()

        success = sum(1 for r in run.results if r.success)
        total = len(run.results)
        self.logger.info(
            f"Run {run.run_id} complete: {success}/{total} successful "
            f"({run.success_rate:.0%}) | Layers: {run.layer_distribution}"
        )

        return run

    async def run_platform(
        self,
        platform: Platform,
        addresses: list[Address],
        store_groups: list[StoreGroup],
    ) -> list[ScrapedResult]:
        """Scrape one platform across all addresses and store groups."""
        scraper = self._create_scraper(platform)
        if not scraper:
            return []

        results: list[ScrapedResult] = []
        # Circuit breaker: track last N results
        cb_window = self.scraper_config.circuit_breaker_window
        cb_threshold = self.scraper_config.circuit_breaker_threshold
        recent_results: deque[bool] = deque(maxlen=cb_window)
        platform_paused = False

        try:
            await scraper.setup()

            for addr_idx, address in enumerate(addresses):
                if platform_paused:
                    self.logger.warning(
                        f"[{platform.value}] CIRCUIT BREAKER: skipping {address.label}"
                    )
                    continue

                for sg in store_groups:
                    product_names = [p.canonical_name for p in sg.products]

                    result = await scraper.scrape_address(
                        address=address,
                        store_type=sg.store_type,
                        store_name=sg.store_name,
                        product_names=product_names,
                    )
                    results.append(result)

                    # Track for circuit breaker
                    recent_results.append(result.success)

                    if result.success:
                        self.logger.info(
                            f"[bold green]OK[/bold green] "
                            f"{platform.value} | {address.label} | "
                            f"{sg.store_type.value} | "
                            f"{len(result.items)} items | "
                            f"layer={result.scrape_layer.value}"
                        )
                    else:
                        self.logger.warning(
                            f"FAIL {platform.value} | {address.label} | "
                            f"{sg.store_type.value} | {result.error_message}"
                        )

                    # Rate limit between stores
                    await scraper.rate_limit_delay()

                # Check circuit breaker after each address
                if len(recent_results) >= cb_window:
                    fail_rate = 1 - (sum(recent_results) / len(recent_results))
                    if fail_rate >= cb_threshold:
                        self.logger.error(
                            f"[{platform.value}] CIRCUIT BREAKER: "
                            f"{fail_rate:.0%} failures in last {cb_window} "
                            f"attempts, pausing platform"
                        )
                        platform_paused = True

                # Log progress
                self.logger.info(
                    f"[{platform.value}] Progress: "
                    f"{addr_idx + 1}/{len(addresses)} addresses"
                )

        except Exception as e:
            self.logger.error(f"[{platform.value}] Fatal error: {e}")
        finally:
            await scraper.teardown()

        return results

    def _save_raw_results(
        self,
        platform: Platform,
        results: list[ScrapedResult],
        run_id: str,
    ) -> None:
        """Save raw results as JSON."""
        paths = self.config.get_paths()
        raw_dir = Path(paths["raw_data"])
        raw_dir.mkdir(parents=True, exist_ok=True)

        ts = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{platform.value}_{ts}.json"

        data = {
            "run_id": run_id,
            "platform": platform.value,
            "timestamp": ts,
            "results_count": len(results),
            "success_count": sum(1 for r in results if r.success),
            "results": [r.model_dump(mode="json") for r in results],
        }

        filepath = raw_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        self.logger.info(f"[{platform.value}] Raw data saved: {filepath}")

    async def normalize_and_merge(
        self,
        run: ScrapingRun,
        output_dir: str = "data/merged",
    ) -> str:
        """Normalize results and merge to CSV."""
        products = self.config.get_products()
        matcher = ProductMatcher(products)
        normalizer = DataNormalizer(product_matcher=matcher)
        validator = DataValidator()
        merger = DataMerger(validator=validator)

        # Normalize product names
        normalizer.normalize_results(run.results)

        # Merge to CSV
        csv_path = merger.merge_to_csv(run.results, output_dir=output_dir)
        return csv_path
