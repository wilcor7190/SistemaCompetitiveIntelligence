# Estrategia de README por MVP

## Concepto

Cada MVP tiene un README en la raiz del proyecto que refleja el estado actual del sistema. El README evoluciona con el proyecto: no es un documento final, es un documento vivo que el evaluador puede leer en cualquier momento.

---

## README por MVP

### MVP 0 — PoC Rappi (v0.1.0-alpha)

```markdown
# Competitive Intelligence System — PoC

Sistema de inteligencia competitiva para plataformas de delivery en Mexico.

## Estado actual: PoC (Proof of Concept)
- ✅ Scraping funcional para Rappi (1 plataforma)
- ✅ 1 direccion de prueba en CDMX
- ✅ 3 productos fast food de McDonald's
- ✅ Sistema de 3 capas de recoleccion (API → DOM → Vision AI)

## Quick Start
  cd desarrollo
  pip install -r requirements.txt
  playwright install chromium
  python -m src.main --debug

## Output
  data/raw/rappi_*.json — Datos crudos

## Stack
  Python 3.10+ | Playwright | Ollama (qwen3-vl, qwen3.5)
```

### MVP 1 — Rappi Multi-Address (v0.1.0)

```markdown
# Competitive Intelligence System

Sistema de inteligencia competitiva para plataformas de delivery en Mexico.
Recolecta datos de precios, fees, tiempos y promociones de 25 direcciones en CDMX.

## Estado actual: MVP 1 — Single Platform
- ✅ Rappi: 25 direcciones, 6 productos (fast food + retail)
- ✅ 3 capas de recoleccion con fallback automatico
- ✅ Normalizacion con embeddings (nomic-embed-text)
- ✅ Output: JSON + CSV

## Quick Start
  cd desarrollo
  pip install -r requirements.txt
  playwright install chromium
  
  # Run completo (25 dirs, ~10 min)
  python -m src.main --platforms rappi
  
  # Test rapido (1 dir, ~30s)
  python -m src.main --debug

## Output
  data/raw/rappi_*.json      — Datos crudos por run
  data/merged/comparison.csv — CSV consolidado

## Metricas Recolectadas
  1. Precio producto (MXN)
  2. Delivery fee
  3. Tiempo de entrega estimado
  4. Promociones activas
  5. Disponibilidad
```

### MVP 2 — Multi-Platform (v0.2.0)

```markdown
# Competitive Intelligence System

Sistema de inteligencia competitiva que compara Rappi, Uber Eats y DiDi Food
en 25 direcciones de CDMX con 6 productos de referencia.

## Estado actual: MVP 2 — Multi-Platform
- ✅ Rappi: scraping completo
- ✅ Uber Eats: scraping completo
- ⚠️ DiDi Food: parcial (Capa 3 vision)
- ✅ 25 direcciones × 3 plataformas × 6 productos
- ✅ Normalizacion y merge a CSV unificado

## Quick Start
  cd desarrollo
  pip install -r requirements.txt
  playwright install chromium
  ollama pull qwen3-vl:8b && ollama pull nomic-embed-text
  
  # Run completo (~30 min)
  python -m src.main
  
  # Solo 2 plataformas (~20 min)
  python -m src.main --platforms rappi,uber_eats
  
  # Test rapido
  python -m src.main --debug

## Output
  data/raw/*.json            — JSON por plataforma y run
  data/merged/comparison.csv — Dataset consolidado
  data/screenshots/          — Evidencia visual

## Metricas
  | Metrica | Rappi | Uber Eats | DiDi Food |
  |---------|-------|-----------|-----------|
  | Precio  | ✅    | ✅        | ⚠️       |
  | Fee     | ✅    | ✅        | ⚠️       |
  | Tiempo  | ✅    | ✅        | ⚠️       |
  | Promos  | ✅    | ⚠️       | ❌       |
  | Disp.   | ✅    | ✅        | ⚠️       |
```

### MVP 3 — Insights & Report (v0.3.0)

```markdown
# Competitive Intelligence System

Sistema completo de inteligencia competitiva: scraping multi-plataforma +
insights generados por IA + visualizaciones + reporte HTML.

## Estado actual: MVP 3 — Insights
- ✅ 3 plataformas scrapeadas
- ✅ 5 insights accionables generados por LLM local (qwen3.5:9b)
- ✅ 4 visualizaciones (barras, heatmap, scatter, tabla)
- ✅ Reporte HTML autocontenido
- ✅ Jupyter notebook reproducible

## Quick Start
  cd desarrollo
  pip install -r requirements.txt
  playwright install chromium
  ollama pull qwen3-vl:8b && ollama pull qwen3.5:9b && ollama pull nomic-embed-text
  
  # Run completo: scraping + insights + reporte (~35 min)
  python -m src.main
  
  # Solo reporte (con datos existentes, ~2 min)
  python -m src.main --report-only
  
  # Usar datos pre-scrapeados (~2 min)
  python -m src.main --use-backup

## Output
  data/merged/comparison.csv     — Dataset consolidado
  reports/insights.html          — Reporte principal (abrir en browser)
  reports/charts/                — Graficos PNG
  notebooks/analysis.ipynb       — Notebook reproducible

## Insights Generados
  1. Posicionamiento de precios — Rappi vs competencia
  2. Ventaja operacional — Tiempos y cobertura
  3. Estructura de fees — Delivery fees comparativos
  4. Estrategia promocional — Promos de la competencia
  5. Variabilidad geografica — Diferencias por zona CDMX

## Arquitectura
  3 capas de recoleccion (API interception → DOM parsing → Vision AI)
  4 modelos Ollama locales (cero costo de APIs externas)
  Ver diseno/arquitectura/ para diagramas detallados
```

### MVP 4 — Polish & Demo Ready (v0.4.0)

```markdown
# 🔍 Competitive Intelligence System for Delivery Platforms

> Sistema automatizado de inteligencia competitiva que recolecta datos de
> Rappi, Uber Eats y DiDi Food en Mexico para generar insights accionables.

## Highlights
- **3 plataformas** comparadas en tiempo real
- **25 direcciones** en 5 zonas de CDMX
- **6 productos** de referencia (fast food + retail + farmacia)
- **5 insights** accionables generados por IA local
- **3 capas de recoleccion** con fallback automatico
- **Cero costo** de APIs externas

## Quick Start

### Requisitos
- Python 3.10+
- Ollama instalado y corriendo (https://ollama.ai)

### Setup (2 minutos)
  git clone <repo>
  cd desarrollo
  python -m venv venv
  source venv/Scripts/activate   # Windows
  pip install -r requirements.txt
  playwright install chromium
  ollama pull qwen3-vl:8b
  ollama pull qwen3.5:9b
  ollama pull nomic-embed-text

### Ejecucion
  # Run completo
  python -m src.main
  
  # Demo rapida (~30s)
  python -m src.main --debug
  
  # Solo insights (datos existentes)
  python -m src.main --report-only

### Ver resultados
  Abrir reports/insights.html en el browser

## Arquitectura

  ┌─────────┐     ┌────────────┐     ┌──────────┐     ┌──────────┐
  │ Config  │────▶│ Scraping   │────▶│ Process  │────▶│ Insights │
  │ JSON/   │     │ 3 Capas    │     │ Normalize│     │ LLM +    │
  │ YAML    │     │ + Fallback │     │ + Match  │     │ Charts   │
  └─────────┘     └────────────┘     └──────────┘     └──────────┘

### 3 Capas de Recoleccion
  1. API Interception — Intercepta APIs internas (rapido, limpio)
  2. DOM Parsing — Selectores CSS + LLM fallback (clasico)
  3. Vision AI — Screenshot + OCR con qwen3-vl (siempre funciona)

### Modelos Ollama
  | Modelo | Funcion |
  |--------|---------|
  | qwen3-vl:8b | OCR de screenshots (Capa 3) |
  | qwen3.5:9b | Generacion de insights |
  | nomic-embed-text | Matching de productos |

## Estructura del Proyecto
  desarrollo/
  ├── src/scrapers/     — Scrapers por plataforma
  ├── src/processors/   — Normalizacion y merge
  ├── src/analysis/     — Insights y visualizaciones
  ├── config/           — Direcciones, productos, settings
  ├── data/             — Datos generados
  └── reports/          — Reportes HTML + charts

## Limitaciones Conocidas
  - Service fee no accesible sin simular compra (ver ADR-003)
  - DiDi Food cobertura parcial
  - Datos de un punto en el tiempo (no tendencia temporal)

## Decisiones Tecnicas
  Ver diseno/decisiones/ para ADRs detallados

## Licencia
  Proyecto de evaluacion tecnica. No distribuir.
```

---

## Regla de Actualizacion

```
Cada vez que se completa un MVP:
  1. Actualizar README.md en la raiz del proyecto
  2. El README refleja SOLO lo que funciona en ese momento
  3. No prometer features que no estan implementadas
  4. Mantener Quick Start actualizado y funcional
  5. El evaluador debe poder copiar/pegar el Quick Start y que funcione
```

---

## Donde Vive el README

```
SistemaCompetitiveIntelligence/
├── README.md              ← README principal (se actualiza por MVP)
├── desarrollo/
│   └── README.md          ← README tecnico (setup, tests, development)
└── diseno/
    └── documentacion/
        └── readme-por-mvp.md  ← ESTE ARCHIVO (plantillas por MVP)
```
