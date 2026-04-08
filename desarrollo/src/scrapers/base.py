"""BaseScraper: abstract class with 3-layer scraping logic."""

import asyncio
import random
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path

from playwright.async_api import Browser, Page, async_playwright

from src.config import ScraperConfig
from src.models.schemas import (
    Address,
    FeeInfo,
    Platform,
    ScrapeLayer,
    ScrapedItem,
    ScrapedResult,
    StoreType,
    TimeEstimate,
)
from src.utils.logger import get_logger


class BaseScraper(ABC):
    """Abstract base for platform scrapers with 3-layer fallback.

    Layer 1: API interception (network response parsing)
    Layer 2: DOM parsing (CSS selectors)
    Layer 3: Vision fallback (screenshot + OCR) — stub in MVP 0
    """

    def __init__(self, config: ScraperConfig, platform: Platform):
        self.config = config
        self.platform = platform
        self.logger = get_logger()
        self._browser: Browser | None = None
        self._page: Page | None = None
        self._playwright = None
        self._intercepted_data: list[dict] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def setup(self) -> None:
        """Launch Playwright browser with stealth settings."""
        self._playwright = await async_playwright().start()

        launch_args = {
            "headless": self.config.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        }

        self._browser = await self._playwright.chromium.launch(**launch_args)

        context_args: dict = {
            "viewport": {
                "width": self.config.viewport_width,
                "height": self.config.viewport_height,
            },
            "user_agent": self.config.user_agent,
            "locale": self.config.locale,
            "timezone_id": self.config.timezone,
        }

        context = await self._browser.new_context(**context_args)

        # Basic stealth: remove navigator.webdriver flag
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        self._page = await context.new_page()
        self._page.set_default_timeout(self.config.page_load_timeout)

        self.logger.info(
            f"[{self.platform.value}] Browser launched "
            f"(headless={self.config.headless})"
        )

    async def teardown(self) -> None:
        """Close browser and cleanup."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._page = None
        self._playwright = None
        self.logger.info(f"[{self.platform.value}] Browser closed")

    @property
    def page(self) -> Page:
        assert self._page is not None, "Call setup() before using the page"
        return self._page

    # ------------------------------------------------------------------
    # 3-Layer scraping
    # ------------------------------------------------------------------

    async def scrape_address(
        self,
        address: Address,
        store_type: StoreType,
        store_name: str | None,
        product_names: list[str],
    ) -> ScrapedResult:
        """Scrape one store at one address, trying 3 layers in order."""
        start = time.time()
        self.logger.info(
            f"[{self.platform.value}][{address.label}] "
            f"Scraping {store_name or store_type.value}..."
        )

        # Try Layer 1 → 2 → 3
        for attempt in range(self.config.max_retries + 1):
            try:
                result = await self._try_all_layers(
                    address, store_type, store_name, product_names
                )
                result.scrape_duration_seconds = time.time() - start
                return result
            except Exception as e:
                self.logger.warning(
                    f"[{self.platform.value}][{address.label}] "
                    f"Attempt {attempt + 1} failed: {e}"
                )
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay)

        # All retries failed
        duration = time.time() - start
        self.logger.error(
            f"[{self.platform.value}][{address.label}] "
            f"All layers failed after {self.config.max_retries + 1} attempts"
        )
        return ScrapedResult(
            platform=self.platform,
            address=address,
            store_type=store_type,
            store_name=store_name or store_type.value,
            scrape_layer=ScrapeLayer.DOM,
            success=False,
            error_message="All layers failed after retries",
            scrape_duration_seconds=duration,
        )

    async def _try_all_layers(
        self,
        address: Address,
        store_type: StoreType,
        store_name: str | None,
        product_names: list[str],
    ) -> ScrapedResult:
        """Try Layer 1 (API) → Layer 2 (DOM) → Layer 3 (Vision)."""

        # Navigate to the store page first
        nav_ok = await self.set_address(address)
        if not nav_ok:
            self.logger.warning(
                f"[{self.platform.value}] Failed to set address: {address.label}"
            )

        search_ok = await self.search_store(store_type, store_name)
        if not search_ok:
            return ScrapedResult(
                platform=self.platform,
                address=address,
                store_type=store_type,
                store_name=store_name or store_type.value,
                scrape_layer=ScrapeLayer.DOM,
                success=False,
                error_message="Store not found",
            )

        # Layer 1: API interception
        api_data = await self.try_api_interception()
        if api_data:
            self.logger.info(
                f"[{self.platform.value}][{address.label}] "
                f"Layer 1 (API) succeeded"
            )
            return self._build_result(
                address, store_type, store_name, api_data, ScrapeLayer.API
            )

        # Layer 2: DOM parsing
        dom_data = await self.try_dom_parsing(product_names)
        if dom_data:
            self.logger.info(
                f"[{self.platform.value}][{address.label}] "
                f"Layer 2 (DOM) succeeded"
            )
            return self._build_result(
                address, store_type, store_name, dom_data, ScrapeLayer.DOM
            )

        # Layer 3: Vision fallback (stub in MVP 0)
        screenshot_path = await self.take_screenshot(
            f"{self.platform.value}_{address.label}"
        )
        vision_data = await self.try_vision_fallback(screenshot_path)
        if vision_data:
            self.logger.info(
                f"[{self.platform.value}][{address.label}] "
                f"Layer 3 (Vision) succeeded"
            )
            result = self._build_result(
                address, store_type, store_name, vision_data, ScrapeLayer.VISION
            )
            result.screenshot_path = screenshot_path
            return result

        # All layers failed for this attempt
        return ScrapedResult(
            platform=self.platform,
            address=address,
            store_type=store_type,
            store_name=store_name or store_type.value,
            scrape_layer=ScrapeLayer.DOM,
            success=False,
            error_message="All 3 layers failed",
            screenshot_path=screenshot_path,
        )

    def _build_result(
        self,
        address: Address,
        store_type: StoreType,
        store_name: str | None,
        data: dict,
        layer: ScrapeLayer,
    ) -> ScrapedResult:
        """Build ScrapedResult from extracted data dict."""
        items = data.get("items", [])
        fees_data = data.get("fees", {})
        time_data = data.get("time_estimate", {})

        return ScrapedResult(
            platform=self.platform,
            address=address,
            store_type=store_type,
            store_name=data.get("store_name", store_name or store_type.value),
            store_id=data.get("store_id"),
            store_url=data.get("store_url", str(self.page.url)),
            items=[ScrapedItem(**i) if isinstance(i, dict) else i for i in items],
            fees=FeeInfo(**fees_data) if isinstance(fees_data, dict) else fees_data,
            time_estimate=(
                TimeEstimate(**time_data)
                if isinstance(time_data, dict)
                else time_data
            ),
            rating=data.get("rating"),
            scrape_layer=layer,
            success=True,
        )

    # ------------------------------------------------------------------
    # Layer implementations (overridable)
    # ------------------------------------------------------------------

    async def try_api_interception(self) -> dict | None:
        """Layer 1: Check intercepted network responses for useful data.

        Override in subclass for platform-specific API patterns.
        Returns dict with keys: items, fees, time_estimate, store_name, etc.
        """
        if self._intercepted_data:
            return self._intercepted_data[-1]
        return None

    async def try_dom_parsing(self, product_names: list[str]) -> dict | None:
        """Layer 2: Extract data from DOM using CSS selectors.

        Delegates to abstract extract_* methods implemented by each platform.
        """
        try:
            items = await self.extract_items(product_names)
            if not items:
                return None

            fees = await self.extract_fees()
            time_est = await self.extract_delivery_time()

            return {
                "items": items,
                "fees": fees.model_dump() if isinstance(fees, FeeInfo) else fees,
                "time_estimate": (
                    time_est.model_dump()
                    if isinstance(time_est, TimeEstimate)
                    else time_est
                ),
                "store_url": str(self.page.url),
            }
        except Exception as e:
            self.logger.warning(
                f"[{self.platform.value}] DOM parsing failed: {e}"
            )
            return None

    async def try_vision_fallback(
        self, screenshot_path: str | None
    ) -> dict | None:
        """Layer 3: Screenshot + OCR with vision LLM."""
        if not screenshot_path:
            return None

        try:
            from src.scrapers.vision_fallback import VisionFallback
            from src.utils.ollama_client import OllamaClient

            client = OllamaClient()
            if not await client.is_available():
                self.logger.debug(
                    "[vision] Ollama not available, skipping Layer 3"
                )
                return None

            vision = VisionFallback(client)
            return await vision.extract_from_screenshot(
                screenshot_path,
                platform_name=self.platform.value,
            )
        except Exception as e:
            self.logger.debug(f"[vision] Layer 3 failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    async def take_screenshot(self, name: str) -> str | None:
        """Capture a screenshot of the current page."""
        try:
            slug = re.sub(r"[^a-zA-Z0-9_-]", "-", name).strip("-")[:80]
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{slug}_{ts}.png"
            screenshots_dir = Path("data/screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            path = screenshots_dir / filename
            await self.page.screenshot(path=str(path), full_page=False)
            self.logger.debug(f"Screenshot saved: {path}")
            return str(path)
        except Exception as e:
            self.logger.warning(f"Screenshot failed: {e}")
            return None

    async def rate_limit_delay(self) -> None:
        """Random delay between requests per settings."""
        delay = random.uniform(self.config.delay_min, self.config.delay_max)
        self.logger.debug(f"Rate limit delay: {delay:.1f}s")
        await asyncio.sleep(delay)

    # ------------------------------------------------------------------
    # Abstract methods — each platform must implement
    # ------------------------------------------------------------------

    @abstractmethod
    async def set_address(self, address: Address) -> bool:
        """Configure the delivery address on the platform."""
        ...

    @abstractmethod
    async def search_store(
        self, store_type: StoreType, store_name: str | None
    ) -> bool:
        """Navigate to the specified store."""
        ...

    @abstractmethod
    async def extract_items(
        self, product_names: list[str]
    ) -> list[ScrapedItem]:
        """Extract product prices from the current page."""
        ...

    @abstractmethod
    async def extract_fees(self) -> FeeInfo:
        """Extract delivery fees and promotions."""
        ...

    @abstractmethod
    async def extract_delivery_time(self) -> TimeEstimate:
        """Extract delivery time estimate."""
        ...

    @abstractmethod
    def get_platform_selectors(self) -> dict[str, str]:
        """Return CSS selectors specific to this platform."""
        ...

    @abstractmethod
    def get_base_url(self) -> str:
        """Return the platform's base URL."""
        ...
