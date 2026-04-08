---
name: desarrollo
description: >
  Fase de desarrollo e implementacion de codigo Python.
  Trigger: Cuando se implementa cualquier modulo en src/, se escribe
  codigo de procesamiento de datos, o se trabaja en la CLI.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Implementing any Python module in src/"
    - "Processing scraped data with pandas"
    - "Refactoring code"
    - "Working on CLI or main.py"
    - "Working on files in desarrollo/"
    - "Documenting scraping progress or technical notes"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

## When to Use

1. Writing or modifying any Python file in `desarrollo/src/`
2. Implementing data processing pipelines
3. Working on the CLI interface

## Critical Patterns

### Code Style
- Python 3.10+ (use `X | None` not `Optional[X]`)
- Type hints on all function signatures
- Async/await for scraper methods
- Docstrings only on public APIs, not every function
- Use `rich` for console output and logging

### Module Structure
```
desarrollo/
├── src/
│   ├── scrapers/     → Use `scraping` skill instead
│   ├── models/       → Pydantic dataclasses only
│   ├── processors/   → Pure functions, no side effects
│   ├── analysis/     → Use `insights` skill instead
│   ├── utils/        → Small, focused helpers
│   ├── config.py     → Single source of config loading
│   └── main.py       → CLI with argparse, minimal logic
├── config/           → JSON/YAML configuration
├── tests/            → pytest tests
├── data/             → Scraped data output
├── reports/          → Generated reports
└── notebooks/        → Jupyter analysis
```

### Error Handling
- Scraping errors: log and continue (never crash the full run)
- Config errors: fail fast with clear message
- Data errors: validate with Pydantic, log invalid records

### Imports
```python
# Standard library first
import asyncio
import json
from pathlib import Path

# Third party
import pandas as pd
from playwright.async_api import async_playwright
from pydantic import BaseModel

# Local
from src.models.schemas import ScrapedResult
from src.utils.logger import logger
```

## Decision Tree

- New scraper code? → Use `scraping` skill
- New visualization? → Use `insights` skill
- New data model? → Add to `desarrollo/src/models/schemas.py`
- New processor? → Add to `desarrollo/src/processors/`, keep functions pure
- New utility? → Does it already exist? Check `desarrollo/src/utils/` first

## Documentation Directory

Development docs go in `desarrollo/` (separate from source code in `src/`).

- `desarrollo/AGENTS.md` → Local agent guidelines for this folder
- `desarrollo/guias/` → Implementation guides per scraper/component
- `desarrollo/progreso/` → MVP progress logs (mvp0-poc.md, mvp1-single-platform.md...)
- `desarrollo/notas-tecnicas/` → API endpoints, CSS selectors, anti-bot findings
- `desarrollo/troubleshooting/` → Problems encountered and solutions

See [desarrollo/AGENTS.md](../../desarrollo/AGENTS.md) for full structure and naming conventions.

## Commands

```bash
# Run the main scraper (from desarrollo/)
cd desarrollo
python -m src.main

# Run with debug mode
python -m src.main --debug

# Run specific platform
python -m src.main --platform uber_eats

# Lint
ruff check src/
ruff format src/
```
