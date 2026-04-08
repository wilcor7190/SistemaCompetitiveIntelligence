"""DiDiFoodScraper: scraper for didi-food.com/es-MX."""

import json
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

DIDI_FOOD_SELECTORS = {
    "restaurant_name": ".store-name, .shop-name, h1",
    "restaurant_rating": ".store-rating, .shop-rating",
    "delivery_time": ".delivery-time, .eta",
    "delivery_fee": ".delivery-fee, .shipping-fee",
    "product_card": ".food-item, .menu-item, .product-card",
    "product_name": ".food-name, .item-name, .product-name",
    "product_price": ".food-price, .item-price, .product-price",
    "search_input": "input[type='search'], .search-input",
    "login_modal": ".login-modal, .login-wrapper, [class*='login']",
    "login_close": ".login-close, .modal-close, button[class*='close']",
}

DIDI_FOOD_API_PATTERNS = [
    r"food\.didi-food\.com/api/",
    r"food-api\.didi-food\.com/",
    r"/store/detail",
    r"/menu/list",
    r"/search/",
]


class DiDiFoodScraper(BaseScraper):
    """Scraper for DiDi Food Mexico (didi-food.com).

    DiDi Food is the hardest platform to scrape:
    - SPA vanilla (no SSR)
    - Requires localStorage for address
    - May require login
    - High probability of falling to Layer 3 (vision)
    """

    BASE_URL = "https://www.didi-food.com"

    def __init__(self, config: ScraperConfig):
        super().__init__(config, Platform.DIDI_FOOD)

    def get_base_url(self) -> str:
        return self.BASE_URL

    def get_platform_selectors(self) -> dict[str, str]:
        return DIDI_FOOD_SELECTORS

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    async def set_address(self, address: Address) -> bool:
        """Inject address into localStorage (DiDi's method)."""
        try:
            context = self.page.context
            await context.set_geolocation(
                {"latitude": address.lat, "longitude": address.lng}
            )
            await context.grant_permissions(["geolocation"])

            # Navigate to DiDi Food first
            await self.page.goto(
                f"{self.BASE_URL}/es-MX/food/",
                wait_until="domcontentloaded",
            )
            await self.page.wait_for_timeout(3000)

            # Inject address into localStorage
            address_data = {
                "lat": address.lat,
                "lng": address.lng,
                "address": address.full_address or address.label,
                "city": address.city,
            }
            await self.page.evaluate(
                f"localStorage.setItem('pl', JSON.stringify({json.dumps(address_data)}))"
            )
            await self.page.reload()
            await self.page.wait_for_timeout(3000)

            self.logger.info(f"[didi_food] Address set via localStorage")
            return True

        except Exception as e:
            self.logger.warning(f"[didi_food] Failed to set address: {e}")
            return False

    async def search_store(
        self, store_type: StoreType, store_name: str | None
    ) -> bool:
        """Search for a store on DiDi Food."""
        if store_type not in (StoreType.RESTAURANT, StoreType.CONVENIENCE):
            return False

        # Try to dismiss login modal if present
        await self._dismiss_login()

        # Try to find McDonald's or search for it
        search_term = store_name or "McDonald's"
        self.logger.info(f"[didi_food] Searching for '{search_term}'")

        try:
            self._intercepted_data.clear()
            self.page.on("response", self._on_response)

            # Try search URL
            await self.page.goto(
                f"{self.BASE_URL}/es-MX/food/search?q={search_term}",
                wait_until="domcontentloaded",
            )
            await self.page.wait_for_timeout(5000)

            # Look for any store link in results
            store_link = await self.page.query_selector(
                "a[href*='/store/'], a[href*='/food/store/']"
            )
            if store_link:
                href = await store_link.get_attribute("href")
                if href:
                    full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    self.logger.info(f"[didi_food] Found store: {full_url}")
                    await self.page.goto(full_url, wait_until="domcontentloaded")
                    await self.page.wait_for_timeout(5000)
                    return True

            # Check if we have any content at all
            body_text = await self.page.evaluate(
                "() => (document.body.innerText || '').substring(0, 500)"
            )
            if len(body_text) > 100:
                self.logger.info("[didi_food] Page has content, attempting extraction")
                return True

            self.logger.warning("[didi_food] No store found")
            return False

        except PlaywrightTimeout:
            self.logger.warning("[didi_food] Timeout during search")
            return False
        except Exception as e:
            self.logger.warning(f"[didi_food] Search failed: {e}")
            return False

    async def _dismiss_login(self) -> None:
        """Try to close login modal if present."""
        try:
            close_btn = await self.page.query_selector(
                ".login-close, .modal-close, button[class*='close'], "
                "[aria-label='close'], [aria-label='cerrar']"
            )
            if close_btn:
                await close_btn.click()
                await self.page.wait_for_timeout(500)
                self.logger.debug("[didi_food] Dismissed login modal")
        except Exception:
            pass

    async def _on_response(self, response) -> None:
        """Intercept API responses."""
        url = response.url
        if not any(re.search(p, url) for p in DIDI_FOOD_API_PATTERNS):
            return
        try:
            if "json" in (response.headers.get("content-type", "")):
                data = await response.json()
                self._intercepted_data.append(data)
                self.logger.debug(f"[didi_food] Intercepted API: {url[:100]}")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    async def extract_items(
        self, product_names: list[str]
    ) -> list[ScrapedItem]:
        """Extract products from DiDi Food DOM via body text parsing."""
        items: list[ScrapedItem] = []

        raw_products = await self.page.evaluate(r"""() => {
            const body = document.body.innerText || '';
            const results = [];
            const lines = body.split('\n').map(l => l.trim()).filter(l => l);

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const priceMatch = line.match(/^\$\s*([\d,.]+)/);
                if (priceMatch) {
                    const price = parseFloat(priceMatch[1].replace(',', '.'));
                    if (price > 0 && price < 5000) {
                        let name = null;
                        for (let j = i - 1; j >= Math.max(0, i - 3); j--) {
                            const candidate = lines[j];
                            if (candidate.length > 3 && candidate.length < 100
                                && !candidate.startsWith('$')
                                && !candidate.match(/^\d+$/)) {
                                name = candidate;
                                break;
                            }
                        }
                        if (name) {
                            results.push({name, price});
                        }
                    }
                }
            }
            return results;
        }""")

        self.logger.info(f"[didi_food] Found {len(raw_products)} products in DOM")

        norm_targets = [n.lower().replace("-", " ") for n in product_names]
        for prod in raw_products:
            original_name = prod["name"]
            price = prod["price"]
            if not price or price <= 0:
                continue

            name_norm = original_name.lower().replace("-", " ")
            matched = None
            for i, target in enumerate(norm_targets):
                if target in name_norm or name_norm in target:
                    matched = product_names[i]
                    break

            items.append(
                ScrapedItem(
                    name=matched or original_name,
                    original_name=original_name,
                    price=price,
                    category="fast_food",
                    available=True,
                )
            )

        matched_count = len([i for i in items if i.name != i.original_name])
        self.logger.info(
            f"[didi_food] Extracted {len(items)} items ({matched_count} matched)"
        )
        return items

    async def extract_fees(self) -> FeeInfo:
        """Extract delivery fee from DiDi Food."""
        try:
            body = await self.page.evaluate("() => document.body.innerText || ''")
            fee_match = re.search(
                r"[Ee]nv[ií]o[:\s]*\$?\s*([\d,.]+)", body
            )
            if fee_match:
                return FeeInfo(
                    delivery_fee=float(fee_match.group(1).replace(",", ".")),
                    delivery_fee_original=fee_match.group(0),
                )
            if "envío gratis" in body.lower() or "envio gratis" in body.lower():
                return FeeInfo(delivery_fee=0.0, delivery_fee_original="Envio Gratis")
        except Exception as e:
            self.logger.debug(f"[didi_food] Fee extraction error: {e}")

        return FeeInfo()

    async def extract_delivery_time(self) -> TimeEstimate:
        """Extract delivery time from DiDi Food."""
        try:
            body = await self.page.evaluate("() => document.body.innerText || ''")
            range_match = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*min", body)
            if range_match:
                return TimeEstimate(
                    min_minutes=int(range_match.group(1)),
                    max_minutes=int(range_match.group(2)),
                    original_text=range_match.group(0),
                )
            single_match = re.search(r"(\d+)\s*min", body)
            if single_match:
                val = int(single_match.group(1))
                return TimeEstimate(
                    min_minutes=val, max_minutes=val,
                    original_text=single_match.group(0),
                )
        except Exception as e:
            self.logger.debug(f"[didi_food] Time extraction error: {e}")

        return TimeEstimate()
