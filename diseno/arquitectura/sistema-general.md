# Sistema General - Arquitectura de 3 Capas

## Diagrama General del Sistema

```mermaid
graph TB
    subgraph CONFIG["CONFIGURACION"]
        A["addresses.json<br/>25-30 direcciones CDMX"]
        B["products.json<br/>5 productos referencia"]
        C["settings.yaml<br/>Rate limits, timeouts, modelos"]
    end

    subgraph ORCHESTRATOR["ORQUESTADOR"]
        D["main.py<br/>CLI Entry Point"]
        E["ScrapingOrchestrator<br/>Coordina plataformas y direcciones"]
    end

    subgraph SCRAPERS["SCRAPERS (por plataforma)"]
        F["RappiScraper<br/>rappi.com.mx"]
        G["UberEatsScraper<br/>ubereats.com/mx"]
        H["DiDiFoodScraper<br/>didi-food.com"]
    end

    subgraph LAYER1["CAPA 1: API Interception"]
        I1["Playwright Network Listener<br/>page.on('response')"]
        I2["API Discovery<br/>Detecta endpoints internos"]
        I3["Direct API Call<br/>aiohttp requests"]
    end

    subgraph LAYER2["CAPA 2: DOM Parsing"]
        J1["Playwright Browser<br/>Headless + Stealth"]
        J2["CSS Selectors<br/>Extraccion estructurada"]
        J3["Text Fallback<br/>qwen3.5:4b parsea texto roto"]
    end

    subgraph LAYER3["CAPA 3: Screenshot + Vision AI"]
        K1["Screenshot Capture<br/>Playwright page.screenshot()"]
        K2["qwen3-vl:8b<br/>OCR inteligente via Ollama"]
        K3["JSON Extraction<br/>Datos estructurados de imagen"]
    end

    subgraph INFRA["INFRAESTRUCTURA"]
        L1["Rate Limiter<br/>3-7s entre requests"]
        L2["Playwright Stealth<br/>Anti-detection"]
        L3["Logger<br/>rich + archivo"]
    end

    subgraph PROCESSING["PROCESAMIENTO"]
        M1["ProductMatcher<br/>nomic-embed-text<br/>Matching semantico"]
        M2["DataNormalizer<br/>Schema unificado"]
        M3["DataValidator<br/>Limpieza y validacion"]
        M4["DataMerger<br/>CSV consolidado"]
    end

    subgraph OUTPUT["SALIDA"]
        N1["data/raw/*.json<br/>JSON por plataforma/run"]
        N2["data/merged/comparison.csv<br/>Dataset consolidado"]
        N3["data/screenshots/<br/>Evidencia visual"]
    end

    subgraph INSIGHTS["GENERACION DE INSIGHTS"]
        O1["pandas Analysis<br/>Estadisticas y comparativas"]
        O2["InsightGenerator<br/>qwen3.5:9b via Ollama"]
        O3["Visualizations<br/>matplotlib + plotly"]
        O4["reports/insights.html<br/>Informe final"]
    end

    A --> D
    B --> D
    C --> D
    D --> E

    E --> F
    E --> G
    E --> H

    F --> I1
    G --> I1
    H --> I1

    I1 --> I2
    I2 -->|"Endpoint encontrado"| I3
    I2 -->|"No encontrado"| J1

    J1 --> J2
    J2 -->|"Selector OK"| M1
    J2 -->|"Selector roto"| J3
    J3 --> M1

    I3 -->|"API OK"| M1
    I3 -->|"Auth requerida"| J1

    J1 -->|"Anti-bot bloquea"| K1
    K1 --> K2
    K2 --> K3
    K3 --> M1

    F -.-> L1
    G -.-> L1
    H -.-> L1
    F -.-> L2
    G -.-> L2
    H -.-> L2

    M1 --> M2
    M2 --> M3
    M3 --> M4
    M3 --> N1
    M4 --> N2
    K1 -.-> N3

    N2 --> O1
    O1 --> O2
    O2 --> O3
    O3 --> O4
```

---

## Descripcion de las 3 Capas de Recoleccion

### Capa 1: API Interception (la mas rapida y estable)

```
Flujo: Playwright navega → intercepta network requests → descubre endpoints API internos
       → llama directo con aiohttp → JSON limpio, rapido, estable

Probabilidad de exito: ~60%
Ideal para: Rappi (Next.js con /_next/data/), Uber Eats (React SPA con APIs internas)
Ventaja: Datos estructurados, rapido, menos detectable
Riesgo: Endpoints pueden requerir auth tokens complejos
```

### Capa 2: Browser Automation + DOM Parsing (la clasica)

```
Flujo: Playwright/Stealth navega como usuario real → espera carga JS
       → extrae con selectores CSS → si falla, qwen3.5:4b parsea texto crudo → JSON

Probabilidad de exito: ~70%
Ideal para: Todas las plataformas como segunda opcion
Ventaja: Simula usuario real, accede a todo lo visible
Riesgo: Anti-bot (Arkose en Uber, reCAPTCHA en Rappi), selectores CSS dinamicos
```

### Capa 3: Screenshot + Vision AI (el Plan B inteligente)

```
Flujo: Playwright captura screenshot de la pagina → qwen3-vl:8b (Ollama local)
       → OCR inteligente → extrae datos como JSON

Probabilidad de exito: ~95%
Ideal para: DiDi Food (SPA pesada), cualquier plataforma cuando Capas 1 y 2 fallan
Ventaja: Siempre funciona si la pagina renderiza, screenshots quedan como EVIDENCIA
Riesgo: Mas lento (~3-5s por imagen), posible perdida de precision en decimales
```

---

## Integracion de Modelos Ollama en el Flujo

```mermaid
graph LR
    subgraph RECOLECCION["Fase: Recoleccion"]
        A["Capa 2 Fallback<br/>qwen3.5:4b"] -->|"Parsea HTML/texto roto"| B["JSON estructurado"]
        C["Capa 3 OCR<br/>qwen3-vl:8b"] -->|"Extrae datos de screenshot"| B
    end

    subgraph NORMALIZACION["Fase: Normalizacion"]
        D["nomic-embed-text"] -->|"Embeddings semanticos"| E["Product Matching<br/>Big Mac = BigMac Individual?"]
    end

    subgraph INSIGHTS_PHASE["Fase: Insights"]
        F["qwen3.5:9b"] -->|"Analiza CSV + genera"| G["5 Insights Accionables<br/>Finding + Impacto + Recomendacion"]
    end

    B --> D
    E --> F
```

| Modelo | Fase | Funcion | RAM | Prioridad |
|--------|------|---------|-----|-----------|
| `qwen3-vl:8b` | Recoleccion (Capa 3) | OCR de screenshots | ~6GB | ALTA |
| `qwen3.5:4b` | Recoleccion (Capa 2 fallback) | Parseo de texto desestructurado | ~3GB | MEDIA |
| `nomic-embed-text` | Normalizacion | Matching semantico de productos | ~0.5GB | MEDIA |
| `qwen3.5:9b` | Insights | Generacion de insights accionables | ~6GB | ALTA |

---

## Componentes y Responsabilidades

| Componente | Ubicacion | Responsabilidad |
|------------|-----------|-----------------|
| **main.py** | `desarrollo/src/main.py` | CLI entry point, parsea argumentos, inicia orquestador |
| **ScrapingOrchestrator** | `desarrollo/src/scrapers/orchestrator.py` | Coordina ejecucion: plataformas × direcciones, maneja fallback entre capas |
| **BaseScraper** | `desarrollo/src/scrapers/base.py` | Clase abstracta con logica comun de las 3 capas |
| **RappiScraper** | `desarrollo/src/scrapers/rappi.py` | Scraper especifico para rappi.com.mx |
| **UberEatsScraper** | `desarrollo/src/scrapers/uber_eats.py` | Scraper especifico para ubereats.com/mx |
| **DiDiFoodScraper** | `desarrollo/src/scrapers/didi_food.py` | Scraper especifico para didi-food.com |
| **VisionFallback** | `desarrollo/src/scrapers/vision_fallback.py` | Capa 3: screenshot + qwen3-vl OCR |
| **TextParser** | `desarrollo/src/scrapers/text_parser.py` | Capa 2 fallback: qwen3.5:4b parsea texto roto |
| **ProductMatcher** | `desarrollo/src/processors/product_matcher.py` | Matching semantico con nomic-embed-text |
| **DataNormalizer** | `desarrollo/src/processors/normalizer.py` | Unifica schemas entre plataformas |
| **DataValidator** | `desarrollo/src/processors/validator.py` | Valida rangos, tipos, completitud |
| **DataMerger** | `desarrollo/src/processors/merger.py` | Genera CSV consolidado |
| **InsightGenerator** | `desarrollo/src/analysis/insights.py` | Genera insights con qwen3.5:9b |
| **Visualizations** | `desarrollo/src/analysis/visualizations.py` | Graficos con matplotlib/plotly |
| **ReportGenerator** | `desarrollo/src/analysis/report_generator.py` | Genera HTML/Jupyter final |
| **Config** | `desarrollo/src/config.py` | Carga y valida configuracion |
| **RateLimiter** | `desarrollo/src/utils/rate_limiter.py` | Control de velocidad entre requests |
| **Logger** | `desarrollo/src/utils/logger.py` | Logging con rich (consola) + archivo |
| **Screenshot** | `desarrollo/src/utils/screenshot.py` | Captura y almacena screenshots |

---

## Flujo End-to-End

```
1. ENTRADA
   Usuario ejecuta: python -m src.main --platforms rappi,uber_eats,didi_food
   Config loader lee: addresses.json, products.json, settings.yaml

2. ORQUESTACION
   ScrapingOrchestrator recibe config
   Para cada plataforma (Rappi → Uber → DiDi):
     Para cada direccion (25-30 en CDMX):
       Intenta Capa 1 → si falla → Capa 2 → si falla → Capa 3
       Guarda ScrapedResult + screenshot opcional
       Rate limit: 3-7s random delay

3. NORMALIZACION
   ProductMatcher usa nomic-embed-text para alinear nombres
   DataNormalizer unifica schema (precios en MXN, tiempos en minutos)
   DataValidator limpia outliers y valida completitud
   DataMerger genera comparison.csv

4. INSIGHTS
   pandas calcula estadisticas (promedios, deltas, variabilidad)
   qwen3.5:9b genera 5 insights: Finding + Impacto + Recomendacion
   matplotlib/plotly genera 3+ visualizaciones
   ReportGenerator empaqueta en HTML

5. SALIDA
   data/raw/          → JSON por plataforma y run
   data/merged/       → comparison.csv consolidado
   data/screenshots/  → Evidencia visual
   reports/           → insights.html + charts/
```
