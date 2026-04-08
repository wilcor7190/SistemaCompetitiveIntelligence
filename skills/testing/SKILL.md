---
name: testing
description: >
  Estrategia y ejecucion de pruebas con pytest.
  Trigger: Cuando se escriben tests, se ejecutan tests,
  se corrige un bug, o se trabaja en tests/.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Writing or running tests"
    - "Writing pytest tests"
    - "Fixing a bug"
    - "Working on files in pruebas/"
    - "Creating test cases or checklists"
    - "Validating data quality"
    - "Preparing for demo or presentation"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

## When to Use

1. Writing new tests in `desarrollo/tests/`
2. Running existing tests
3. Fixing a bug (write failing test first)

## Critical Patterns

### Test File Naming
```
desarrollo/tests/
├── test_scrapers.py          # Scraper unit tests
├── test_normalizer.py        # Data normalizer tests
├── test_models.py            # Pydantic model tests
├── test_config.py            # Config loading tests
└── conftest.py               # Shared fixtures
```

### Test Structure (AAA Pattern)
```python
def test_scraped_item_price_is_positive():
    # Arrange
    item_data = {"name": "Big Mac", "price": 89.0, "currency": "MXN", "available": True}
    
    # Act
    item = ScrapedItem(**item_data)
    
    # Assert
    assert item.price > 0
    assert item.currency == "MXN"
```

### Fixtures for Scraped Data
```python
@pytest.fixture
def sample_scraped_result():
    return ScrapedResult(
        platform="uber_eats",
        address=Address(label="Reforma 222", lat=19.43, lng=-99.13, zone_type="centro"),
        restaurant="McDonald's",
        items=[ScrapedItem(name="Big Mac", price=89.0, currency="MXN", available=True)],
        fees=FeeInfo(delivery_fee=29.0, service_fee=12.0),
        time=TimeEstimate(min_minutes=25, max_minutes=35),
        timestamp="2026-04-07T10:00:00",
        success=True,
    )
```

### What to Test (Priority)
1. **Data models**: Pydantic validation (required)
2. **Normalizer**: Data transformation correctness (required)
3. **Config loading**: Addresses/products parse correctly (required)
4. **Scrapers**: Mock browser, test parsing logic (nice-to-have)
5. **E2E scraping**: Only manual/integration (skip in CI)

### What NOT to Test
- Playwright browser interactions (mock them)
- External API responses (use fixtures)
- Visual chart output (manual verification)

## Documentation Directory

Test documentation and QA artifacts go in `pruebas/` (separate from test code in `tests/`).

- `pruebas/AGENTS.md` → Local agent guidelines for this folder
- `pruebas/casos/` → Test cases documented per component
- `pruebas/reportes/` → Test execution reports (YYYY-MM-DD-run.md)
- `pruebas/evidencia/` → Screenshots, manual validation
- `pruebas/checklists/` → Pre-entrega, pre-demo checklists

See [pruebas/AGENTS.md](../../pruebas/AGENTS.md) for full structure and naming conventions.

## Commands

```bash
# Run all tests (from desarrollo/)
cd desarrollo
pytest tests/ -v

# Run specific test file
pytest tests/test_normalizer.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run only fast tests (no network)
pytest tests/ -v -m "not slow"
```
