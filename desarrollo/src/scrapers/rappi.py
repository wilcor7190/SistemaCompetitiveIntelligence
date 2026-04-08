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

# CSS selectors — verified against real Rappi DOM (2026-04-07)
# Rappi uses Chakra UI + Styled Components (sc-*) with hashed classes
RAPPI_SELECTORS = {
    # Store page — left menu panel
    "restaurant_name": "[data-testid='restaurant'] span[data-testid='typography']",
    "restaurant_rating": "[data-qa='left-menu']",  # parse "4.1" from text
    "delivery_time": "[data-qa='left-menu']",  # parse "35 min" from text
    "delivery_fee": "[data-qa='left-menu']",  # parse "Gratis" from text
    # Products — Chakra UI stack cards with h4 title
    "product_card": "div.chakra-stack[class*='css-']",
    "product_name": "h4.chakra-text",
    "product_price": "span",  # contains "$ 155.00" text
    "product_description": "p.chakra-text",
    # Promotions
    "promo_badge": "[class*='promo'], [class*='discount']",
    "promo_banner": "[class*='promotion'], [class*='campaign']",
    # Address
    "address_input": "[data-qa='input']",
    "address_suggestion": "[data-testid='address-suggestion'], .autocomplete-item",
    # Search
    "search_input": "[data-qa='input']",
    "search_result": "[data-testid='search-result']",
    # Menu categories
    "menu_category": "a[data-testid='menuOption']",
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
        """Extract product items from the DOM.

        Rappi uses Chakra UI: product cards are div.chakra-stack with
        h4.chakra-text for name and spans containing '$ NNN.00' for price.
        """
        items: list[ScrapedItem] = []

        try:
            # Wait for h4 product titles to appear
            await self.page.wait_for_selector(
                "h4.chakra-text",
                timeout=self.config.selector_timeout,
            )
        except PlaywrightTimeout:
            self.logger.warning("[rappi] No product titles found in DOM")
            return items

        # Extract product data using JS for reliability
        raw_products = await self.page.evaluate("""() => {
            const h4s = document.querySelectorAll('h4.chakra-text');
            const results = [];
            for (const h4 of h4s) {
                // Walk up to find the card container with price
                let card = h4.parentElement;
                for (let i = 0; i < 4 && card; i++) {
                    const text = card.innerText || '';
                    if (text.includes('$')) {
                        // Extract all prices from card text
                        const priceMatches = text.match(/\\$\\s*[\\d,.]+/g);
                        if (priceMatches && priceMatches.length > 0) {
                            // First price is the current/discounted price
                            const priceStr = priceMatches[0].replace(/[^\\d.,]/g, '').replace(',', '.');
                            results.push({
                                name: h4.textContent.trim(),
                                price: parseFloat(priceStr),
                                originalPrice: priceMatches.length > 1
                                    ? parseFloat(priceMatches[1].replace(/[^\\d.,]/g, '').replace(',', '.'))
                                    : null,
                                hasDiscount: text.includes('%'),
                            });
                        }
                        break;
                    }
                    card = card.parentElement;
                }
            }
            return results;
        }""")

        self.logger.info(f"[rappi] Found {len(raw_products)} products in DOM")

        lowercase_targets = [n.lower() for n in product_names]

        for prod in raw_products:
            original_name = prod["name"]
            price = prod["price"]

            if not price or price <= 0:
                continue

            # Match against target product names
            name_lower = original_name.lower()
            matched_canonical = None
            for i, target in enumerate(lowercase_targets):
                if target in name_lower or name_lower in target:
                    matched_canonical = product_names[i]
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

        matched_count = len([i for i in items if i.name != i.original_name])
        self.logger.info(
            f"[rappi] Extracted {len(items)} items ({matched_count} matched targets)"
        )
        return items

    async def extract_fees(self) -> FeeInfo:
        """Extract delivery fee and promotions from the left-menu panel.

        Rappi shows fee info in [data-qa='left-menu'] as text like:
        'Envío\\nGratis\\n(nuevos usuarios)' or 'Envío\\n$ 19.00'
        """
        delivery_fee: float | None = None
        delivery_fee_original: str | None = None
        promotions: list[str] = []

        try:
            info = await self.page.evaluate("""() => {
                const menu = document.querySelector('[data-qa="left-menu"]');
                if (!menu) return null;
                const text = menu.innerText || '';
                return text;
            }""")

            if info:
                lines = info.split("\n")
                for i, line in enumerate(lines):
                    line_lower = line.strip().lower()
                    # Find delivery fee
                    if "envío" in line_lower or "envio" in line_lower:
                        # Next line(s) contain the fee value
                        for j in range(i + 1, min(i + 3, len(lines))):
                            next_line = lines[j].strip()
                            if "gratis" in next_line.lower() or "free" in next_line.lower():
                                delivery_fee = 0.0
                                delivery_fee_original = next_line
                                break
                            elif "$" in next_line:
                                delivery_fee = self._parse_price_text(next_line)
                                delivery_fee_original = next_line
                                break

                # Extract promotions from banner area
                promo_text = await self.page.evaluate("""() => {
                    const promos = [];
                    // Look for promo banners above product grid
                    const els = document.querySelectorAll('[class*="promo"], [class*="campaign"], [class*="discount"]');
                    for (const el of els) {
                        const t = (el.innerText || '').trim();
                        if (t && t.length < 100) promos.push(t);
                    }
                    // Also check for banner text with "gratis" or "OFF"
                    const spans = document.querySelectorAll('p[data-testid="typography"]');
                    for (const s of spans) {
                        const t = (s.textContent || '').trim();
                        if (t && (t.toLowerCase().includes('gratis') || t.includes('OFF') || t.includes('%')) && t.length < 100) {
                            promos.push(t);
                        }
                    }
                    return [...new Set(promos)].slice(0, 5);
                }""")
                promotions = promo_text or []

        except Exception as e:
            self.logger.debug(f"[rappi] Fee extraction error: {e}")

        return FeeInfo(
            delivery_fee=delivery_fee,
            delivery_fee_original=delivery_fee_original,
            promotions=promotions,
        )

    async def extract_delivery_time(self) -> TimeEstimate:
        """Extract delivery time from the left-menu panel.

        Rappi shows time as '35 min' in [data-qa='left-menu'].
        """
        try:
            info = await self.page.evaluate("""() => {
                const menu = document.querySelector('[data-qa="left-menu"]');
                if (!menu) return null;
                return menu.innerText || '';
            }""")

            if info:
                # Look for "NN min" pattern in the menu text
                match = re.search(r"(\d+)\s*min", info)
                if match:
                    minutes = int(match.group(1))
                    return TimeEstimate(
                        min_minutes=minutes,
                        max_minutes=minutes,
                        original_text=f"{minutes} min",
                    )
                # Look for range "NN-NN min"
                range_match = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*min", info)
                if range_match:
                    return TimeEstimate(
                        min_minutes=int(range_match.group(1)),
                        max_minutes=int(range_match.group(2)),
                        original_text=range_match.group(0),
                    )
        except Exception as e:
            self.logger.debug(f"[rappi] Time extraction error: {e}")

        return TimeEstimate()

    async def try_dom_parsing(self, product_names: list[str]) -> dict | None:
        """Override to include rating extraction."""
        result = await super().try_dom_parsing(product_names)
        if result:
            result["rating"] = await self._extract_rating()
            result["store_name"] = "McDonald's"
            result["store_id"] = self._current_store_id
        return result

    async def _extract_rating(self) -> float | None:
        """Extract restaurant rating from left-menu panel."""
        try:
            info = await self.page.evaluate("""() => {
                const menu = document.querySelector('[data-qa="left-menu"]');
                if (!menu) return null;
                return menu.innerText || '';
            }""")
            if info:
                # Look for pattern like "Calificación\n4.1"
                match = re.search(r"[Cc]alificaci[oó]n\s*\n?\s*(\d+\.?\d*)", info)
                if match:
                    return float(match.group(1))
        except Exception:
            pass
        return None

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
