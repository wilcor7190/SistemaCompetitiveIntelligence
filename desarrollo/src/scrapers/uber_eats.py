"""UberEatsScraper: scraper for ubereats.com/mx."""

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

# Known McDonald's store URLs from spike
MCDONALDS_URLS = {
    "polanco": "/mx/store/mcdonalds-polanco/GMcH3w_vX4CtLxBPRICeWA",
    "reforma": "/mx/store/mcdonalds-reforma/yD_69FtxTTGWjKm4rJ1BEg",
}

# Brand page for listing all McDonald's locations
MCDONALDS_BRAND_PAGE = "/mx/brand-city/mexico-city-df/mcdonalds"

UBER_EATS_SELECTORS = {
    "restaurant_name": "h1[data-testid='store-title'], h1",
    "restaurant_rating": "[data-testid='store-rating']",
    "delivery_time": "[data-testid='store-delivery-time'], [class*='delivery-time']",
    "delivery_fee": "[data-testid='store-delivery-fee'], [class*='delivery-fee']",
    "product_card": "[data-testid='store-item'], li[class*='menu-item']",
    "product_name": "[data-testid='rich-text'], span[class*='name']",
    "product_price": "span[class*='price'], [data-testid='rich-text'] + span",
    "address_button": "[data-testid='address-selector'], button[aria-label*='address']",
    "address_input": "[data-testid='address-input'], input[placeholder*='address']",
    "address_suggestion": "[data-testid='address-suggestion']",
    "arkose_frame": "iframe[src*='arkoselabs'], iframe[src*='funcaptcha']",
    "store_card": "[data-testid='store-card'], a[class*='store']",
}

UBER_EATS_API_PATTERNS = [
    r"/api/getStoreV1",
    r"/api/getMenuV1",
    r"/api/getFeedV1",
    r"/marketplace/graphql",
    r"/eats/v\d+/stores",
    r"/eats/v\d+/menu",
]


class UberEatsScraper(BaseScraper):
    """Scraper for Uber Eats Mexico (ubereats.com/mx)."""

    BASE_URL = "https://www.ubereats.com"

    def __init__(self, config: ScraperConfig):
        super().__init__(config, Platform.UBER_EATS)
        self._arkose_detected = False

    def get_base_url(self) -> str:
        return self.BASE_URL

    def get_platform_selectors(self) -> dict[str, str]:
        return UBER_EATS_SELECTORS

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    async def set_address(self, address: Address) -> bool:
        """Set geolocation for the address."""
        try:
            context = self.page.context
            await context.set_geolocation(
                {"latitude": address.lat, "longitude": address.lng}
            )
            await context.grant_permissions(["geolocation"])
            return True
        except Exception as e:
            self.logger.debug(f"[uber_eats] Geolocation failed: {e}")
            return True

    async def search_store(
        self, store_type: StoreType, store_name: str | None
    ) -> bool:
        """Navigate to a store on Uber Eats."""
        if store_type == StoreType.RESTAURANT:
            return await self._navigate_to_restaurant(store_name)
        elif store_type == StoreType.CONVENIENCE:
            return await self._navigate_to_convenience(store_name)
        self.logger.warning(
            f"[uber_eats] Store type {store_type.value} not implemented"
        )
        return False

    async def _navigate_to_restaurant(self, name: str | None) -> bool:
        """Navigate to McDonald's via brand page."""
        # Try brand page first (lists all locations)
        url = f"{self.BASE_URL}{MCDONALDS_BRAND_PAGE}"
        self.logger.info(f"[uber_eats] Navigating to brand page: {url}")

        try:
            self._intercepted_data.clear()
            self.page.on("response", self._on_response)

            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)

            # Check for Arkose challenge
            if await self._check_arkose():
                return False

            # Try to click first store from brand page
            store_link = await self.page.query_selector(
                "a[href*='/store/mcdonalds'], a[href*='/mx/store/']"
            )
            if store_link:
                href = await store_link.get_attribute("href")
                if href:
                    store_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    self.logger.info(f"[uber_eats] Found store: {store_url}")
                    await self.page.goto(store_url, wait_until="domcontentloaded")
                    await self.page.wait_for_timeout(3000)

                    if await self._check_arkose():
                        return False

                    return True

            # Fallback: try direct known URL
            direct_url = f"{self.BASE_URL}{MCDONALDS_URLS['polanco']}"
            self.logger.info(f"[uber_eats] Fallback to direct URL: {direct_url}")
            await self.page.goto(direct_url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)

            if await self._check_arkose():
                return False

            return True

        except PlaywrightTimeout:
            self.logger.warning("[uber_eats] Timeout navigating")
            return False
        except Exception as e:
            self.logger.warning(f"[uber_eats] Navigation failed: {e}")
            return False

    async def _navigate_to_convenience(self, name: str | None) -> bool:
        """Navigate to Oxxo/convenience on Uber Eats."""
        url = f"{self.BASE_URL}/mx/brand-city/mexico-city-df/oxxo"
        self.logger.info(f"[uber_eats] Navigating to Oxxo brand page")

        try:
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)

            if await self._check_arkose():
                return False

            store_link = await self.page.query_selector(
                "a[href*='/store/'], a[href*='/mx/store/']"
            )
            if store_link:
                href = await store_link.get_attribute("href")
                if href:
                    store_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    await self.page.goto(store_url, wait_until="domcontentloaded")
                    await self.page.wait_for_timeout(3000)
                    return not await self._check_arkose()

            return False

        except Exception as e:
            self.logger.warning(f"[uber_eats] Convenience navigation failed: {e}")
            return False

    async def _check_arkose(self) -> bool:
        """Check if Arkose/botdefense challenge is present."""
        arkose = await self.page.query_selector(
            "iframe[src*='arkoselabs'], iframe[src*='funcaptcha'], "
            "[class*='captcha'], [id*='captcha']"
        )
        if arkose:
            self._arkose_detected = True
            self.logger.warning(
                "[uber_eats] Arkose challenge detected, falling back to Layer 3"
            )
            return True
        return False

    async def _on_response(self, response) -> None:
        """Intercept API responses."""
        url = response.url
        if not any(re.search(p, url) for p in UBER_EATS_API_PATTERNS):
            return
        try:
            if "json" in (response.headers.get("content-type", "")):
                data = await response.json()
                self._intercepted_data.append(data)
                self.logger.debug(f"[uber_eats] Intercepted API: {url[:100]}")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    async def extract_items(
        self, product_names: list[str]
    ) -> list[ScrapedItem]:
        """Extract products from Uber Eats DOM."""
        items: list[ScrapedItem] = []

        # Try to extract via JS body text parsing (most reliable)
        raw_products = await self.page.evaluate(r"""() => {
            const body = document.body.innerText || '';
            const results = [];
            // Uber Eats shows menu items with names and prices
            // Pattern: product name on one line, price like $NNN.NN nearby
            const lines = body.split('\n').map(l => l.trim()).filter(l => l);

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                // Check if this line looks like a price
                const priceMatch = line.match(/^\$\s*([\d,.]+)/);
                if (priceMatch) {
                    const price = parseFloat(priceMatch[1].replace(',', '.'));
                    if (price > 0 && price < 5000) {
                        // Look backward for the product name (usually 1-3 lines before)
                        let name = null;
                        for (let j = i - 1; j >= Math.max(0, i - 3); j--) {
                            const candidate = lines[j];
                            if (candidate.length > 3 && candidate.length < 100
                                && !candidate.startsWith('$')
                                && !candidate.match(/^\d+$/)
                                && !candidate.match(/^(Agregar|Add|Ver|Nuevo|Popular)/i)) {
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

        self.logger.info(f"[uber_eats] Found {len(raw_products)} products in DOM")

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
            f"[uber_eats] Extracted {len(items)} items ({matched_count} matched)"
        )
        return items

    async def extract_fees(self) -> FeeInfo:
        """Extract delivery fee from Uber Eats."""
        delivery_fee = None
        delivery_fee_original = None
        promotions: list[str] = []

        try:
            body = await self.page.evaluate("() => document.body.innerText || ''")
            # Look for delivery fee pattern
            fee_match = re.search(
                r"[Dd]elivery\s*[Ff]ee[:\s]*\$?\s*([\d,.]+)", body
            )
            if fee_match:
                delivery_fee = float(fee_match.group(1).replace(",", "."))
                delivery_fee_original = fee_match.group(0)
            elif "free delivery" in body.lower() or "envío gratis" in body.lower():
                delivery_fee = 0.0
                delivery_fee_original = "Free Delivery"

            # Promotions
            promo_patterns = [
                r"(free delivery[^.]*)",
                r"(\d+%\s*off[^.]*)",
                r"(buy \d+ get \d+[^.]*)",
                r"(spend \$\d+[^.]*free[^.]*)",
            ]
            for pattern in promo_patterns:
                for m in re.finditer(pattern, body, re.IGNORECASE):
                    promotions.append(m.group(1).strip())

        except Exception as e:
            self.logger.debug(f"[uber_eats] Fee extraction error: {e}")

        return FeeInfo(
            delivery_fee=delivery_fee,
            delivery_fee_original=delivery_fee_original,
            promotions=promotions[:5],
        )

    async def extract_delivery_time(self) -> TimeEstimate:
        """Extract delivery time from Uber Eats."""
        try:
            body = await self.page.evaluate("() => document.body.innerText || ''")
            # Pattern: "25-35 min" or "35 min"
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
            self.logger.debug(f"[uber_eats] Time extraction error: {e}")

        return TimeEstimate()
