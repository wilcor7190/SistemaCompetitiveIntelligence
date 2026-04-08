# Competitive Intelligence System — PoC

Sistema de inteligencia competitiva para plataformas de delivery en Mexico.

## Estado actual: PoC (Proof of Concept)

- ✅ Scraping funcional para Rappi (1 plataforma)
- ✅ 1 direccion de prueba en CDMX
- ✅ 3 productos fast food de McDonald's
- ✅ Sistema de 3 capas de recoleccion (API → DOM → Vision AI)

## Quick Start

```bash
cd desarrollo
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
playwright install chromium
python -m src.main --debug
```

## Output

```
data/raw/rappi_*.json — Datos crudos
```

## Tests

```bash
cd desarrollo
pytest tests/ -v
```

## Stack

Python 3.10+ | Playwright | Pydantic | Rich | Ollama (qwen3-vl, qwen3.5)

## Estructura

```
desarrollo/src/
├── scrapers/base.py    — BaseScraper con 3 capas (API → DOM → Vision)
├── scrapers/rappi.py   — RappiScraper para rappi.com.mx
├── models/schemas.py   — Modelos Pydantic (Address, ScrapedItem, etc.)
├── utils/logger.py     — Logger con rich
├── utils/ollama_client.py — Wrapper async para Ollama
├── config.py           — Config loader (YAML + JSON)
└── main.py             — CLI con --debug
```

## Documentacion

- `Analisis/` — Requerimientos y analisis de mercado
- `diseno/` — Arquitectura, schemas, ADRs, selectores CSS
- `pruebas/` — Casos de prueba, checklists, reportes

## Licencia

Proyecto de evaluacion tecnica. No distribuir.
