"""RappiScraper: scraper for rappi.com.mx."""

import re

from playwright.async_api import TimeoutError as PlaywrightTimeout

from src.config import ScraperConfig
from src.models.schemas import (
    Address,
    FeeInfo,
    Platform,
    ScrapedItem,
    StoreType,
    TimeEstimate,
)
from src.scrapers.base import BaseScraper

# Known McDonald's store IDs from spike
MCDONALDS_STORE_IDS = [
    "1306705702",  # McDonald's Alvaro Obregon
    "1306705685",  # McDonald's Centro
    "1306718166",  # McDonald's Juarez
    "1923200225",  # McDonald's Supmz 7
]

# CSS selectors — estimates from design docs, need verification with DevTools
RAPPI_SELECTORS = {
    # Store page
    "restaurant_name": "[data-testid='store-name'], h1.store-name, .restaurant-header h1, h1",
    "restaurant_rating": "[data-testid='store-rating'], .store-rating, .rating-value",
    "delivery_time": "[data-testid='delivery-time'], .delivery-time, .eta-text, [class*='eta'], [class*='time']",
    "delivery_fee": "[data-testid='delivery-fee'], .delivery-fee, .shipping-cost, [class*='delivery-fee'], [class*='shipping']",
    # Products
    "product_card": "[data-testid='product-card'], .product-card, .menu-item, [class*='product-item'], [class*='menu-item']",
    "product_name": "[data-testid='product-name'], .product-name, .item-name, h3, span[class*='name']",
    "product_price": "[data-testid='product-price'], .product-price, .item-price, span[class*='price']",
    # Promotions
    "promo_badge": "[data-testid='promo-badge'], .promo-badge, .discount-badge, [class*='promo'], [class*='discount']",
    "promo_banner": ".promo-banner, .store-promotion, .campaign-banner, [class*='promotion']",
    # Address
    "address_input": "[data-testid='address-input'], input[placeholder*='recibir'], input[placeholder*='dirección']",
    "address_suggestion": "[data-testid='address-suggestion'], .address-suggestion, .autocomplete-item",
    # Search
    "search_input": "[data-testid='search-input'], input[placeholder*='Buscar'], input[type='search']",
    "search_result": "[data-testid='search-result'], .search-result-item",
}

# API patterns to intercept
RAPPI_API_PATTERNS = [
    r"/_next/data/.+/restaurantes/.+\.json",
    r"/api/(?:v\d+/)?(?:store|restaurant|menu)",
    r"/graphql",
    r"services\.rappi\.com",
    r"microservices\.rappi\.com",
]


class RappiScraper(BaseScraper):
    """Scraper for Rappi Mexico (rappi.com.mx)."""

    BASE_URL = "https://www.rappi.com.mx"

    def __init__(self, config: ScraperConfig):
        super().__init__(config, Platform.RAPPI)
        self._current_store_id: str | None = None

    def get_base_url(self) -> str:
        return self.BASE_URL

    def get_platform_selectors(self) -> dict[str, str]:
        return RAPPI_SELECTORS

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    async def set_address(self, address: Address) -> bool:
        """For MVP 0: navigate directly to store URL (skip address input)."""
        # MVP 0 uses direct store URLs, no address configuration needed
        self.logger.debug(
            f"[rappi][{address.label}] Using direct URL navigation"
        )
        return True

    async def search_store(
        self, store_type: StoreType, store_name: str | None
    ) -> bool:
        """Navigate to the store page.

        MVP 0: Direct URL navigation to McDonald's with known store IDs.
        """
        if store_type == StoreType.RESTAURANT:
            return await self._navigate_to_restaurant(store_name)
        # Convenience and pharmacy stubs for MVP 0
        self.logger.warning(
            f"[rappi] Store type {store_type.value} not implemented in MVP 0"
        )
        return False

    async def _navigate_to_restaurant(self, name: str | None) -> bool:
        """Navigate to a restaurant by direct URL."""
        store_id = MCDONALDS_STORE_IDS[0]
        url = f"{self.BASE_URL}/restaurantes/{store_id}-mcdonalds"
        self._current_store_id = store_id

        self.logger.info(f"[rappi] Navigating to {url}")

        try:
            # Set up API interception before navigation
            self._intercepted_data.clear()
            self.page.on("response", self._on_response)

            await self.page.goto(url, wait_until="domcontentloaded")
            # Wait for content to render
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(2000)

            self.logger.info(
                f"[rappi] Page loaded: {self.page.url}"
            )
            return True
        except PlaywrightTimeout:
            self.logger.warning(f"[rappi] Timeout navigating to {url}")
            return False
        except Exception as e:
            self.logger.warning(f"[rappi] Navigation failed: {e}")
            return False

    async def _on_response(self, response) -> None:
        """Intercept network responses for Layer 1 (API)."""
        url = response.url
        if not any(re.search(p, url) for p in RAPPI_API_PATTERNS):
            return
        try:
            if "json" in (response.headers.get("content-type", "")):
                data = await response.json()
                self._intercepted_data.append(data)
                self.logger.debug(f"[rappi] Intercepted API: {url[:100]}")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Extraction — Layer 2 (DOM)
    # ------------------------------------------------------------------

    async def extract_items(
        self, product_names: list[str]
    ) -> list[ScrapedItem]:
        """Extract product items from the DOM."""
        items: list[ScrapedItem] = []
        selectors = self.get_platform_selectors()

        try:
            # Wait for product cards to appear
            await self.page.wait_for_selector(
                selectors["product_card"],
                timeout=self.config.selector_timeout,
            )
        except PlaywrightTimeout:
            self.logger.warning("[rappi] No product cards found in DOM")
            return items

        cards = await self.page.query_selector_all(selectors["product_card"])
        self.logger.info(f"[rappi] Found {len(cards)} product cards")

        lowercase_targets = [n.lower() for n in product_names]

        for card in cards:
            try:
                name_el = await card.query_selector(
                    selectors["product_name"]
                )
                price_el = await card.query_selector(
                    selectors["product_price"]
                )

                if not name_el or not price_el:
                    continue

                original_name = (await name_el.inner_text()).strip()
                price_text = (await price_el.inner_text()).strip()
                price = self._parse_price_text(price_text)

                if price is None or price <= 0:
                    continue

                # Check if this product matches any of our targets
                name_lower = original_name.lower()
                matched_canonical = None
                for target in lowercase_targets:
                    if target in name_lower or name_lower in target:
                        # Find the original-cased canonical name
                        idx = lowercase_targets.index(target)
                        matched_canonical = product_names[idx]
                        break

                items.append(
                    ScrapedItem(
                        name=matched_canonical or original_name,
                        original_name=original_name,
                        price=price,
                        category="fast_food",
                        available=True,
                    )
                )
            except Exception as e:
                self.logger.debug(f"[rappi] Error parsing card: {e}")
                continue

        self.logger.info(
            f"[rappi] Extracted {len(items)} items "
            f"({len([i for i in items if i.name != i.original_name])} matched)"
        )
        return items

    async def extract_fees(self) -> FeeInfo:
        """Extract delivery fee and promotions from DOM."""
        selectors = self.get_platform_selectors()
        delivery_fee: float | None = None
        delivery_fee_original: str | None = None
        promotions: list[str] = []

        # Try to find delivery fee
        try:
            fee_el = await self.page.query_selector(selectors["delivery_fee"])
            if fee_el:
                fee_text = (await fee_el.inner_text()).strip()
                delivery_fee_original = fee_text
                if "gratis" in fee_text.lower() or "free" in fee_text.lower():
                    delivery_fee = 0.0
                else:
                    delivery_fee = self._parse_price_text(fee_text)
        except Exception as e:
            self.logger.debug(f"[rappi] Fee extraction error: {e}")

        # Try to find promotions
        try:
            promo_els = await self.page.query_selector_all(
                selectors["promo_badge"]
            )
            for el in promo_els[:5]:  # Limit to avoid noise
                text = (await el.inner_text()).strip()
                if text and len(text) < 100:
                    promotions.append(text)

            banner_els = await self.page.query_selector_all(
                selectors["promo_banner"]
            )
            for el in banner_els[:3]:
                text = (await el.inner_text()).strip()
                if text and len(text) < 100:
                    promotions.append(text)
        except Exception as e:
            self.logger.debug(f"[rappi] Promo extraction error: {e}")

        return FeeInfo(
            delivery_fee=delivery_fee,
            delivery_fee_original=delivery_fee_original,
            promotions=promotions,
        )

    async def extract_delivery_time(self) -> TimeEstimate:
        """Extract delivery time estimate from DOM."""
        selectors = self.get_platform_selectors()

        try:
            time_el = await self.page.query_selector(
                selectors["delivery_time"]
            )
            if time_el:
                text = (await time_el.inner_text()).strip()
                min_min, max_min = self._parse_time_text(text)
                return TimeEstimate(
                    min_minutes=min_min,
                    max_minutes=max_min,
                    original_text=text,
                )
        except Exception as e:
            self.logger.debug(f"[rappi] Time extraction error: {e}")

        return TimeEstimate()

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_price_text(text: str) -> float | None:
        """Parse price from text like '$155.00', 'MXN 155', '155'."""
        if not text:
            return None
        # Remove currency symbols and whitespace
        cleaned = re.sub(r"[^\d.,]", "", text)
        if not cleaned:
            return None
        # Handle comma as decimal separator
        cleaned = cleaned.replace(",", ".")
        # Take first valid number
        match = re.search(r"\d+\.?\d*", cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None

    @staticmethod
    def _parse_time_text(text: str) -> tuple[int | None, int | None]:
        """Parse time from text like '25-35 min', '35 min', '~40 min'."""
        if not text:
            return None, None
        # Look for range pattern: "25-35 min"
        range_match = re.search(r"(\d+)\s*[-–a]\s*(\d+)", text)
        if range_match:
            return int(range_match.group(1)), int(range_match.group(2))
        # Look for single number: "35 min"
        single_match = re.search(r"(\d+)", text)
        if single_match:
            val = int(single_match.group(1))
            return val, val
        return None, None
