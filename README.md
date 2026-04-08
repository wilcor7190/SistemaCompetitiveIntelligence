# Competitive Intelligence System

Sistema de inteligencia competitiva para plataformas de delivery en Mexico.
Recolecta datos de precios, fees, tiempos y promociones de 25 direcciones en CDMX.

## Estado actual: MVP 1 — Single Platform

- ✅ Rappi: 25 direcciones, 3 productos fast food (McDonald's)
- ✅ 3 capas de recoleccion con fallback automatico
- ✅ Normalizacion con product matching por aliases
- ✅ Output: JSON raw + CSV consolidado
- ✅ 94 tests automatizados

## Quick Start

```bash
cd desarrollo
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
playwright install chromium

# Run completo (25 dirs, ~10 min)
python -m src.main --platforms rappi

# Test rapido (1 dir, ~30s)
python -m src.main --debug

# Solo 3 direcciones
python -m src.main --platforms rappi --max-addresses 3 --headless

# Ver plan sin ejecutar
python -m src.main --dry-run
```

## Output

```
data/raw/rappi_*.json          — Datos crudos por run
data/merged/comparison_*.csv   — CSV consolidado
data/screenshots/              — Capturas de evidencia
```

## Tests

```bash
cd desarrollo
pytest tests/ -v     # 94 tests
```

## Metricas Recolectadas

1. Precio producto (MXN)
2. Delivery fee
3. Tiempo de entrega estimado
4. Promociones activas
5. Disponibilidad
6. Rating del restaurante

## Arquitectura

```
desarrollo/src/
├── scrapers/
│   ├── base.py              — BaseScraper: 3 capas (API -> DOM -> Vision)
│   ├── rappi.py             — RappiScraper: McDonald's + convenience
│   ├── orchestrator.py      — Loop addresses x stores con circuit breaker
│   ├── vision_fallback.py   — Capa 3: screenshot + qwen3-vl OCR
│   └── text_parser.py       — Capa 2 fallback: qwen3.5:4b
├── processors/
│   ├── normalizer.py        — Parseo precios, fees, tiempos
│   ├── product_matcher.py   — Alias lookup + embeddings
│   ├── validator.py         — Validacion de rangos
│   └── merger.py            — Flatten a CSV con deduplicacion
├── models/schemas.py        — 12 modelos Pydantic
├── utils/                   — Logger (rich), Ollama client, rate limiter
├── config.py                — Config loader (YAML + JSON)
└── main.py                  — CLI con 10+ flags
```

## Stack

Python 3.10+ | Playwright | Pydantic | pandas | Rich | Ollama (qwen3-vl, qwen3.5)

## Documentacion

- `Analisis/` — Requerimientos y analisis de mercado
- `diseno/` — Arquitectura, schemas, ADRs, selectores CSS
- `pruebas/` — Casos de prueba, checklists, reportes por MVP

## Limitaciones

- Solo 1 plataforma (Rappi) — Uber Eats y DiDi Food en MVP 2
- Convenience stores (Oxxo/Turbo) con cobertura parcial
- Capas 2-fallback y 3 requieren Ollama corriendo

## Licencia

Proyecto de evaluacion tecnica. No distribuir.
