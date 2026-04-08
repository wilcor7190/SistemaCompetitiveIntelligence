---
name: scraping
description: >
  Patrones de web scraping con Playwright, Nodriver y API interception.
  Trigger: Cuando se escribe codigo de scraper, se configura browser
  automation, se manejan anti-bot, o se extraen datos de delivery platforms.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Writing scraper code (Playwright, Nodriver, requests)"
    - "Working with Playwright browser automation"
    - "Handling anti-bot detection"
    - "Extracting data from delivery platforms"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

## When to Use

1. Implementing any scraper in `desarrollo/src/scrapers/`
2. Dealing with anti-bot detection or browser stealth
3. Intercepting network requests or APIs from delivery platforms

## Critical Patterns

### Scraper Class Pattern
Every scraper extends `BaseScraper`:
```python
class UberEatsScraper(BaseScraper):
    PLATFORM = "uber_eats"
    BASE_URL = "https://www.ubereats.com/mx"
    
    async def set_address(self, address: Address) -> bool:
        # Platform-specific address setting
        ...
    
    async def search_restaurant(self, name: str) -> bool:
        # Platform-specific restaurant search
        ...
    
    async def extract_items(self, product_names: list[str]) -> list[ScrapedItem]:
        # Platform-specific price extraction
        ...
    
    async def extract_fees(self) -> FeeInfo:
        # Platform-specific fee extraction
        ...
```

### Stealth Configuration (Non-negotiable)
```python
# Always use these Playwright settings
browser = await playwright.chromium.launch(
    headless=True,
    args=['--disable-blink-features=AutomationControlled']
)
context = await browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    locale='es-MX',
    timezone_id='America/Mexico_City',
)
# Remove webdriver flag
await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
```

### Rate Limiting (Non-negotiable)
```python
import random
import asyncio

async def respectful_delay():
    """Random delay between 3-7 seconds."""
    delay = random.uniform(3, 7)
    await asyncio.sleep(delay)
```

### Network Interception (Preferred for APIs)
```python
async def intercept_api(page):
    """Capture API responses for direct data extraction."""
    api_data = []
    
    async def handle_response(response):
        if '/api/' in response.url and response.status == 200:
            try:
                data = await response.json()
                api_data.append(data)
            except:
                pass
    
    page.on('response', handle_response)
    return api_data
```

## Decision Tree

- Can I get data via API interception?
  → YES: Use `requests`/`httpx` directly (faster, more stable)
  → NO: Use Playwright browser automation
- Getting blocked by anti-bot?
  → Try: playwright-stealth → proxy rotation → Nodriver → manual data (Plan B)
- Data missing or inconsistent?
  → Log the gap, continue with next address, don't crash
- New platform to scrape?
  → Create `desarrollo/src/scrapers/{platform}.py` extending `BaseScraper`

## Target Platforms

| Platform | URL | Difficulty | Strategy |
|----------|-----|------------|----------|
| Uber Eats | ubereats.com/mx | Medium | API interception preferred |
| Rappi | rappi.com.mx | Medium-High | Playwright + stealth |
| DiDi Food | didi-food.com | Medium | Playwright direct |

## Anti-Bot Escalation Ladder

```
Level 0: Playwright + stealth settings (try first)
Level 1: Add random delays (3-7s) + human-like behavior
Level 2: Rotate User-Agents per request
Level 3: Use ScraperAPI or proxy rotation
Level 4: Switch to Nodriver (better anti-detection)
Level 5: Manual data collection (Plan B)
```

## Commands

```bash
# Install Playwright browsers
playwright install chromium

# Test single scraper
python -c "from src.scrapers.uber_eats import UberEatsScraper; ..."

# Run with screenshots (from desarrollo/)
cd desarrollo
python -m src.main --screenshots
```
