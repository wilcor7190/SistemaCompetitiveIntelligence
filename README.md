# Competitive Intelligence System

Sistema de inteligencia competitiva que compara Rappi, Uber Eats y DiDi Food
en 25 direcciones de CDMX con 6 productos de referencia.

## Estado actual: MVP 3 — Insights + Reporte

- ✅ 3 plataformas scrapeadas (Rappi + Uber Eats + DiDi parcial)
- ✅ 5 insights accionables generados por analisis estadistico
- ✅ 4 visualizaciones (barras, heatmap, scatter, tabla)
- ✅ Reporte HTML autocontenido (reports/insights.html)
- ✅ --report-only para regenerar insights desde datos existentes
- ✅ 130 tests automatizados

## Prerrequisitos

Antes de clonar e instalar, asegurate de tener lo siguiente en tu computador:

| Herramienta | Version minima | Como verificar | Instalacion |
|-------------|---------------|----------------|-------------|
| **Python** | 3.10+ | `python --version` | [python.org/downloads](https://www.python.org/downloads/) |
| **Git** | 2.30+ | `git --version` | [git-scm.com](https://git-scm.com/) |
| **pip** | 21+ | `pip --version` | Viene con Python |
| **Ollama** (opcional) | cualquier | `ollama --version` | [ollama.ai](https://ollama.ai/) |

> **Nota sobre Ollama:** Solo es necesario si quieres usar las capas avanzadas de IA
> (OCR de screenshots y generacion de insights). El scraping basico funciona sin Ollama.

### Sistemas operativos soportados

- **Windows 10/11** (probado) — usar Git Bash o PowerShell
- **macOS** — cambiar `source venv/Scripts/activate` por `source venv/bin/activate`
- **Linux** — cambiar `source venv/Scripts/activate` por `source venv/bin/activate`

## Instalacion paso a paso

```bash
# 1. Clonar el repositorio
git clone https://github.com/wilcor7190/SistemaCompetitiveIntelligence.git
cd SistemaCompetitiveIntelligence

# 2. Ir a la carpeta de desarrollo
cd desarrollo

# 3. Crear entorno virtual de Python
python -m venv venv

# 4. Activar el entorno virtual
source venv/Scripts/activate   # Windows (Git Bash)
# source venv/bin/activate     # macOS / Linux

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Instalar Chromium para Playwright (browser automatizado)
playwright install chromium

# 7. (Opcional) Instalar modelos de Ollama para IA avanzada
# ollama pull qwen3-vl:8b        # OCR de screenshots
# ollama pull qwen3.5:4b         # Parseo de texto
# ollama pull qwen3.5:9b         # Generacion de insights
# ollama pull nomic-embed-text   # Matching de productos
```

## Como ejecutar

Todos los comandos se ejecutan desde la carpeta `desarrollo/` con el venv activado.

### Scraping rapido (1 direccion, ~30 segundos)

```bash
python -m src.main --debug
```

Abre un browser visible, scrapea McDonald's en Rappi y muestra el resultado en consola.

### Scraping multi-plataforma (1 direccion)

```bash
python -m src.main --platforms rappi,uber_eats --max-addresses 1 --headless
```

### Scraping completo (25 direcciones, ~30 min)

```bash
python -m src.main --platforms rappi,uber_eats --headless
```

### Ver plan sin ejecutar

```bash
python -m src.main --dry-run
```

### Guardar backup de datos

```bash
python -m src.main --platforms rappi,uber_eats --max-addresses 3 --headless --save-backup
```

### Todos los flags disponibles

| Flag | Descripcion |
|------|-------------|
| `--platforms rappi,uber_eats,didi_food` | Plataformas a scrapear (separadas por coma) |
| `--max-addresses N` | Limitar a N direcciones (0 = todas) |
| `--debug` | Modo rapido: 1 plataforma, 1 direccion, browser visible |
| `--headless / --no-headless` | Browser visible o invisible |
| `--screenshots` | Capturar screenshots en cada extraccion |
| `--dry-run` | Mostrar plan sin ejecutar |
| `--save-backup` | Guardar copia de datos en data/backup/ |
| `--use-backup` | Usar datos pre-scrapeados en vez de scrapear |
| `--report-only` | Solo generar reporte desde CSV existente |

## Tests

```bash
cd desarrollo
source venv/Scripts/activate

# Ejecutar todos los tests
pytest tests/ -v

# Solo un archivo de tests
pytest tests/test_models.py -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

Resultado esperado: **130 tests passing**.

## Output generado

```
data/raw/*.json                — Datos crudos por plataforma y ejecucion
data/merged/comparison_*.csv   — CSV consolidado con 24 columnas
data/screenshots/              — Capturas de pantalla como evidencia
data/backup/                   — Copias de seguridad (--save-backup)
```

### Columnas del CSV

`timestamp`, `platform`, `address_label`, `zone_type`, `store_type`, `store_name`,
`canonical_product`, `original_product_name`, `price_mxn`, `delivery_fee_mxn`,
`delivery_time_min`, `delivery_time_max`, `promotions`, `rating`, `scrape_layer`, ...

## Datos verificados (2026-04-07)

| Producto | Rappi | Uber Eats |
|----------|-------|-----------|
| Big Mac Tocino | $155 MXN | $204 MXN |
| McNuggets 10 pzas | $145 MXN | $155 MXN |
| Coca-Cola 600ml (Turbo) | $19 MXN | — (Arkose) |
| Delivery fee | Gratis | Por verificar |
| Tiempo entrega | 35 min | 25-35 min |
| Rating | 4.1 | 4.5+ |

## Metricas por plataforma

| Metrica | Rappi | Uber Eats | DiDi Food |
|---------|-------|-----------|-----------|
| Precio  | ✅    | ✅        | ❌        |
| Fee     | ✅    | ✅        | ❌        |
| Tiempo  | ✅    | ✅        | ❌        |
| Promos  | ✅    | ⚠️        | ❌        |
| Rating  | ✅    | ✅        | ❌        |

## Arquitectura

```
desarrollo/src/
├── scrapers/
│   ├── base.py              — BaseScraper: 3 capas (API -> DOM -> Vision)
│   ├── rappi.py             — RappiScraper: restaurant + Turbo convenience
│   ├── uber_eats.py         — UberEatsScraper: brand page + Arkose detection
│   ├── didi_food.py         — DiDiFoodScraper: localStorage + SPA parsing
│   ├── orchestrator.py      — Loop platforms x addresses x stores
│   ├── vision_fallback.py   — Capa 3: screenshot + qwen3-vl OCR
│   └── text_parser.py       — Capa 2 fallback: qwen3.5:4b
├── processors/
│   ├── normalizer.py        — Parseo precios, fees, tiempos
│   ├── product_matcher.py   — Alias lookup + embeddings
│   ├── validator.py         — Validacion de rangos
│   └── merger.py            — CSV con deduplicacion
├── models/schemas.py        — 12 modelos Pydantic
├── utils/                   — Logger, Ollama client, rate limiter
├── config.py                — Config loader (YAML + JSON)
└── main.py                  — CLI
```

### 3 Capas de recoleccion

1. **API Interception** — Intercepta APIs internas de la plataforma (rapido)
2. **DOM Parsing** — Selectores CSS verificados con DevTools (clasico)
3. **Vision AI** — Screenshot + OCR con qwen3-vl (requiere Ollama)

## Documentacion del proyecto

| Carpeta | Contenido |
|---------|-----------|
| `Analisis/` | Requerimientos, analisis de mercado, MVP roadmap |
| `diseno/` | Arquitectura, schemas, ADRs, selectores CSS, CLI spec |
| `pruebas/` | Casos de prueba, checklists, reportes por MVP |
| `desarrollo/` | Codigo fuente, tests, configuracion, datos |

## Limitaciones conocidas

- **DiDi Food**: no produce datos (SPA vanilla sin SSR, posible login requerido). Documentado como limitacion, 2 plataformas priorizadas por calidad.
- **Service fee**: no accesible sin simular compra (ver `diseno/decisiones/ADR-003`)
- **Convenience Uber Eats**: bloqueado por Arkose anti-bot en brand page
- **Capas IA**: Capas 2-fallback y 3 requieren Ollama corriendo localmente

## Stack tecnologico

Python 3.10+ | Playwright | Pydantic | pandas | Rich | aiohttp | PyYAML | Ollama

## Licencia

Proyecto de evaluacion tecnica. No distribuir.
