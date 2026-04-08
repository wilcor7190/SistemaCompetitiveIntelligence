# Competitive Intelligence System for Delivery Platforms

> Sistema automatizado de inteligencia competitiva que recolecta datos de
> Rappi, Uber Eats y DiDi Food en Mexico para generar insights accionables
> con IA (Claude Opus 4.6).

## Highlights

- **3 plataformas** comparadas (Rappi + Uber Eats verificados, DiDi documentado)
- **25 direcciones** en 5 zonas de CDMX
- **6 productos** de referencia (fast food + retail + farmacia)
- **5 insights** accionables (resumen ejecutivo generado por Claude API)
- **4 visualizaciones** (barras, heatmap, scatter, tabla pivot)
- **3 capas de recoleccion** con fallback automatico (API -> DOM -> Vision AI)
- **130 tests** automatizados (100% passing)
- **Costo ultra-bajo**: ~$0.01-$0.05 USD por ejecucion completa con Claude API

## Estado actual: MVP 4 — Production Ready (v0.4.0)

- ✅ Pipeline completo: Scraping -> Normalizacion -> Insights -> Reporte HTML
- ✅ 3 plataformas implementadas (2 funcionales con datos reales, 1 documentada)
- ✅ Sistema resiliente con backup y fallback automatico
- ✅ Migracion completa de Ollama local a Claude API (mas rapido y mejor calidad)
- ✅ Codigo formateado con ruff, linter clean
- ✅ Documentacion completa por fase

## Prerrequisitos

Antes de clonar e instalar, asegurate de tener lo siguiente en tu computador:

| Herramienta | Version minima | Como verificar | Instalacion |
|-------------|---------------|----------------|-------------|
| **Python** | 3.10+ | `python --version` | [python.org/downloads](https://www.python.org/downloads/) |
| **Git** | 2.30+ | `git --version` | [git-scm.com](https://git-scm.com/) |
| **pip** | 21+ | `pip --version` | Viene con Python |
| **Claude API key** (opcional) | - | - | [console.anthropic.com](https://console.anthropic.com/settings/keys) |

> **Nota sobre Claude API:** El sistema funciona **completamente sin API key** —
> los insights se generan con estadisticas (pandas) en modo fallback. Solo se
> necesita la API key para:
> - Generar resumenes ejecutivos profesionales con narrativa de calidad VP
> - Activar Capa 3 (vision OCR) para resiliencia anti-bot avanzada
>
> **Costo aproximado con API key:** $0.01-$0.05 USD por ejecucion completa.
> Anthropic ofrece **$5 USD de credito gratis** al crear cuenta nueva
> (suficiente para ~100 ejecuciones).

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

# 7. (Opcional pero recomendado) Configurar Claude API
cp .env.example .env
# Editar .env y reemplazar el placeholder con tu API key:
#   ANTHROPIC_API_KEY=sk-ant-api03-tu-key-aqui
# Get your key at: https://console.anthropic.com/settings/keys
```

### Como obtener la API key de Claude (1 minuto)

1. Ve a https://console.anthropic.com/settings/keys
2. Inicia sesion (Anthropic regala $5 USD de credito al registrarse)
3. Click en **Create Key**
4. Copia la key (empieza con `sk-ant-`)
5. Pegala en `desarrollo/.env`

> El archivo `.env` esta en `.gitignore` — nunca se sube a GitHub.

## Como ejecutar

Todos los comandos se ejecutan desde la carpeta `desarrollo/` con el venv activado.

### Demo rapida (1 direccion, ~30 segundos)

```bash
python -m src.main --debug
```

Abre un browser visible, scrapea McDonald's en Rappi y muestra el resultado en consola.

### Generar reporte sin scraping (modo backup)

```bash
python -m src.main --use-backup
```

Usa datos pre-scrapeados de `data/backup/` y genera el reporte HTML completo.
**Ideal para demos sin internet** o cuando las plataformas estan bloqueando.

### Solo regenerar el reporte desde un CSV

```bash
python -m src.main --report-only --report-data data/merged/comparison_combined.csv
```

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

### Ver el reporte generado

Abre en tu browser:
```
desarrollo/reports/insights.html
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
| `--report-data` | Ruta al CSV (con --report-only) |

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
reports/insights.html          — Reporte HTML autocontenido (con resumen IA)
reports/charts/                — 4 visualizaciones (PNG + tabla HTML)
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
│   ├── vision_fallback.py   — Capa 3: screenshot + Claude vision
│   └── text_parser.py       — Capa 2 fallback: parseo con Claude API
├── processors/
│   ├── normalizer.py        — Parseo precios, fees, tiempos
│   ├── product_matcher.py   — Alias lookup normalizado
│   ├── validator.py         — Validacion de rangos
│   └── merger.py            — CSV con deduplicacion
├── analysis/
│   ├── insights.py          — 5 insights + resumen ejecutivo (Claude Opus 4.6)
│   ├── visualizations.py    — 4 charts con matplotlib/seaborn
│   └── report_generator.py  — HTML autocontenido (base64 embebido)
├── models/schemas.py        — 12 modelos Pydantic
├── utils/
│   ├── claude_client.py     — Wrapper async para Claude API
│   ├── logger.py            — Logger con rich
│   ├── rate_limiter.py      — Random delays
│   └── screenshot.py        — Captura y naming
├── config.py                — Config loader (YAML + JSON)
└── main.py                  — CLI
```

### 3 Capas de recoleccion

1. **API Interception** — Intercepta APIs internas de la plataforma (rapido)
2. **DOM Parsing** — Selectores CSS verificados con DevTools (clasico)
3. **Vision AI** — Screenshot + Claude vision API (resiliente al cambio de DOM)

### Por que Claude API en lugar de Ollama local?

El proyecto inicialmente uso modelos locales con Ollama (qwen3-vl, qwen3.5),
pero migramos a Claude API por estas razones:

| Aspecto | Ollama (antes) | Claude API (ahora) |
|---------|---------------|-------------------|
| **Velocidad** | Lento (minutos por consulta) | Rapido (~5-10 segundos) |
| **Setup** | Instalar Ollama + descargar 12 GB de modelos | Solo una API key |
| **Calidad insights** | Modelo pequeno (4B params) | Claude Opus 4.6 (estado del arte) |
| **Confiabilidad** | Se colgaba con frecuencia | Consistente |
| **RAM requerida** | 8+ GB libres | Cero (corre en servidores) |
| **Costo** | $0 (gratis local) | ~$0.01-$0.05 USD por ejecucion |
| **Funciona sin API key?** | No | **Si** (fallback stats-based) |

**Resultado**: Resumen ejecutivo de calidad profesional + sistema mas rapido,
ligero y facil de instalar para evaluadores.

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
- **Capa 3 (Vision)**: requiere `ANTHROPIC_API_KEY` configurada en `.env`
- **Insights basicos sin API key**: el sistema funciona pero genera resumen template
  (deterministico) en lugar del narrativo profesional de Claude

## Stack tecnologico

Python 3.10+ | Playwright | Pydantic | pandas | matplotlib | seaborn | Rich
| **Anthropic Claude API (Opus 4.6)** | aiohttp | PyYAML

## Licencia

Proyecto de evaluacion tecnica. No distribuir.
