# Fase: Desarrollo e Implementacion

> Este archivo guia al agente cuando trabaja dentro de `desarrollo/`.
> Overrides sobre el AGENTS.md raiz para esta fase.

## Proposito de esta carpeta

Contiene **TODO** lo relacionado con desarrollo: codigo fuente, tests, configuracion, datos, reportes generados, notebooks y documentacion tecnica.

## Estrategia de Desarrollo

El desarrollo sigue un plan de MVPs incrementales. Cada MVP es funcional por si solo.

| MVP | Branch | Tag | Que se construye |
|-----|--------|-----|-----------------|
| 0 | `feature/poc-rappi` | `v0.1.0-alpha` | schemas, config, base.py, rappi.py, main.py (--debug) |
| 1 | `feature/rappi-scraper` | `v0.1.0` | orchestrator, normalizer, matcher, merger, multi-store |
| 2 | `feature/multi-platform` | `v0.2.0` | uber_eats.py, didi_food.py |
| 3 | `feature/insights-report` | `v0.3.0` | insights.py, visualizations.py, report_generator.py |
| 4 | `release/v0.4.0` | `v0.4.0` | README, cleanup, presentacion |

**Guia completa:** Ver `diseno/guia-ejecucion-mvps.md` para prompts y pasos detallados.
**Plan de MVPs:** Ver `diseno/plan-mvps.md` para scope y criterios de exito.

## Estructura

```
desarrollo/
├── AGENTS.md                    # THIS FILE
│
├── src/                         # Codigo fuente
│   ├── scrapers/                # Scrapers por plataforma
│   │   ├── __init__.py
│   │   ├── base.py              # BaseScraper: 3 capas (API → DOM → Vision)
│   │   ├── orchestrator.py      # ScrapingOrchestrator: dirs × stores × platforms
│   │   ├── rappi.py             # RappiScraper (MVP 0)
│   │   ├── uber_eats.py         # UberEatsScraper (MVP 2)
│   │   ├── didi_food.py         # DiDiFoodScraper (MVP 2)
│   │   ├── vision_fallback.py   # Capa 3: qwen3-vl OCR (MVP 1)
│   │   └── text_parser.py       # Capa 2 fallback: qwen3.5:4b (MVP 1)
│   ├── models/                  # Modelos de datos
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic: Address, ScrapedItem, ScrapedResult, etc.
│   ├── processors/              # Procesamiento de datos (MVP 1)
│   │   ├── __init__.py
│   │   ├── normalizer.py        # Parseo precios/fees/tiempos
│   │   ├── product_matcher.py   # Aliases + nomic-embed-text
│   │   ├── validator.py         # Rangos y completitud
│   │   └── merger.py            # Merge a comparison.csv
│   ├── analysis/                # Insights y visualizaciones (MVP 3)
│   │   ├── __init__.py
│   │   ├── insights.py          # InsightGenerator con qwen3.5:9b
│   │   ├── visualizations.py    # 4 charts matplotlib/plotly
│   │   └── report_generator.py  # HTML autocontenido
│   ├── utils/                   # Utilidades
│   │   ├── __init__.py
│   │   ├── ollama_client.py     # Wrapper async para Ollama
│   │   ├── rate_limiter.py      # Random delays entre requests
│   │   ├── logger.py            # Logging con rich
│   │   └── screenshot.py        # Captura y naming de screenshots
│   ├── __init__.py
│   ├── config.py                # Carga settings.yaml, addresses.json, products.json
│   └── main.py                  # CLI entry point (14 flags, ver cli-spec.md)
│
├── config/                      # Configuracion
│   ├── addresses.json           # 25 direcciones en 5 clusters CDMX
│   ├── products.json            # 6 productos en 3 store_groups (restaurant/convenience/pharmacy)
│   └── settings.yaml            # Scraping, browser, Ollama, proxy, paths, logging
│
├── tests/                       # Tests automatizados (pytest)
│   ├── conftest.py              # Fixtures compartidos
│   ├── test_models.py           # MVP 0: Pydantic schemas
│   ├── test_config.py           # MVP 0: Config loader
│   ├── test_normalizer.py       # MVP 1: Parseo precios/fees/tiempos
│   ├── test_product_matcher.py  # MVP 1: Alias + embedding matching
│   ├── test_merger.py           # MVP 1: CSV generation
│   ├── test_validator.py        # MVP 1: Range validation
│   ├── test_scrapers.py         # MVP 2: Scraper factory, selectors
│   ├── test_integration.py      # MVP 2: Full pipeline mock
│   ├── test_insights.py         # MVP 3: Insight generation
│   ├── test_visualizations.py   # MVP 3: Chart generation
│   └── test_report.py           # MVP 3: HTML report
│
├── data/                        # Datos generados (NO commitear raw/merged/screenshots)
│   ├── raw/                     # JSON por plataforma y run
│   ├── merged/                  # CSV consolidado
│   ├── screenshots/             # Capturas de pantalla
│   └── backup/                  # Datos pre-scrapeados para demo
│
├── reports/                     # Reportes generados
│   ├── charts/                  # PNG de graficos
│   └── insights.html            # Informe final (symlink al mas reciente)
│
├── notebooks/                   # Jupyter notebooks
│   └── analysis.ipynb           # Analisis reproducible (MVP 3)
│
├── guias/                       # Guias de implementacion
├── progreso/                    # Logs de progreso por MVP
├── notas-tecnicas/              # Endpoints, selectores, anti-bot
├── troubleshooting/             # Problemas y soluciones
│
├── requirements.txt             # Dependencias (playwright, ollama, pandas, etc.)
├── .env.example                 # OLLAMA_BASE_URL, SCRAPER_API_KEY, etc.
└── logs/                        # Logs de ejecucion (NO commitear)
```

## Comandos (ejecutar desde desarrollo/)

```bash
# Setup
cd desarrollo
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
playwright install chromium
ollama pull qwen3-vl:8b && ollama pull qwen3.5:9b && ollama pull nomic-embed-text

# Run completo (3 plataformas, 25 dirs, ~30 min)
python -m src.main

# PoC rapido (1 plataforma, 1 dir, ~30s)
python -m src.main --debug

# Solo Rappi
python -m src.main --platforms rappi

# Solo reporte (con datos existentes)
python -m src.main --report-only

# Con datos pre-scrapeados (demo)
python -m src.main --use-backup

# Guardar backup para demo
python -m src.main --save-backup

# Tests
pytest tests/ -v

# Lint
ruff check src/ && ruff format src/
```

## Convenciones de Codigo

### Python Style
- Python 3.10+ (use `X | None` not `Optional[X]`)
- Type hints en todas las funciones publicas
- Async/await para scrapers
- `rich` para logging y output consola

### Imports
```python
# Standard library
import asyncio
import json
from pathlib import Path

# Third party
import pandas as pd
from playwright.async_api import async_playwright
from pydantic import BaseModel
import ollama

# Local
from src.models.schemas import ScrapedResult, Platform, StoreType
from src.utils.logger import logger
from src.utils.ollama_client import OllamaClient
```

### Error Handling
- Scraping errors: log y continuar (NUNCA crashear el run completo)
- 3 capas de fallback: API → DOM → Vision (ver diseno/arquitectura/flujo-datos.md sec 5)
- Circuit breaker: ≥60% fallos en 10 dirs → pausar plataforma
- Config errors: fail fast con mensaje claro
- Ollama no disponible: warning, saltar capas que lo requieren
- LLM JSON invalido: limpiar → retry → regex fallback (ver prompts-ollama.md sec 5)
- Datos: NUNCA descartar. Mejor datos parciales que no datos.

### Multi-Store (ADR-004)
Cada direccion se scrapea en 2-3 tipos de tienda:
1. Restaurant (McDonald's) → Big Mac, McNuggets, Combo
2. Convenience (Oxxo) → Coca-Cola, Agua
3. Pharmacy (farmacia) → Panales (MVP 2+)

## Documentos de Diseno Clave

| Necesitas saber... | Lee... |
|---------------------|--------|
| Arquitectura general | `diseno/arquitectura/sistema-general.md` |
| Como funciona cada capa | `diseno/arquitectura/flujo-datos.md` |
| Modelos Pydantic | `diseno/modelos/schemas.md` |
| Reglas de normalizacion | `diseno/modelos/normalizacion.md` |
| Selectores CSS por plataforma | `diseno/arquitectura/navegacion-plataformas.md` |
| Prompts de Ollama | `diseno/arquitectura/prompts-ollama.md` |
| CLI flags | `diseno/arquitectura/cli-spec.md` |
| Estructura del reporte | `diseno/arquitectura/reporte-estructura.md` |
| Plan de MVPs | `diseno/plan-mvps.md` |
| Guia de ejecucion paso a paso | `diseno/guia-ejecucion-mvps.md` |
| Tolerancia a fallos | `diseno/arquitectura/tolerancia-fallos.md` |

## Skills asociados
- `desarrollo` → Codigo general en src/
- `scraping` → Scrapers en src/scrapers/
- `insights` → Analisis en src/analysis/
- `testing` → Tests en tests/

## Relacion con otras carpetas
- **Analisis/** → Input: requerimientos y scope
- **diseno/** → Input: arquitectura, schemas, prompts, CLIs guian la implementacion
- **pruebas/** → Output: documentacion de QA, checklists, evidencia por MVP
