# Estructura de Presentacion — 30 minutos

## Formato

```
20 min presentacion + 10 min Q&A
```

---

## Guion Minuto a Minuto

### 1. Approach y Scope (3 min)

```
SLIDE 1: Titulo
  "Sistema de Competitive Intelligence para Delivery en Mexico"
  Nombre, fecha, rol: AI Engineer

SLIDE 2: El problema
  "Rappi no tiene visibilidad sistematica de como se compara con la competencia"
  4 preguntas del brief: precios, tiempos, fees, promociones

SLIDE 3: Mi approach
  "No construi un scraper. Construi un SISTEMA DE INTELIGENCIA con 3 capas"
  Diagrama simplificado de las 3 capas (1 slide, no detalle tecnico)
  
  Narrativa clave:
  "Si la capa principal falla, el sistema se adapta automaticamente.
   Los datos se normalizan con embeddings semanticos y los insights
   se generan asistidos por un LLM local. Todo corre sin APIs externas."

SLIDE 4: Scope
  - 3 plataformas: Rappi, Uber Eats, DiDi Food
  - 25 direcciones en 5 zonas de CDMX
  - 6 productos: 3 fast food + 2 retail + 1 farmacia
  - 5 metricas: precio, delivery fee, tiempo, promos, disponibilidad
  - ~375+ data points
```

### 2. Demo del Sistema (7 min)

```
DEMO LIVE: python -m src.main --debug
  - Mostrar el scraper corriendo en tiempo real (1 dir, 1 plataforma, ~30s)
  - Narrar mientras corre: "Aqui esta intentando Capa 1... 
    encontro API... extrayendo precios..."
  - Si falla: "Esto es esperado, por eso tenemos 3 capas"

  Si la demo live funciona: 2 min
  Si falla: "Tengo datos pre-scrapeados" → python -m src.main --use-backup

DEMO OUTPUT: Mostrar archivos generados
  - Terminal: resumen del run (plataformas, success rate, capas usadas)
  - data/raw/*.json → "Datos crudos por plataforma"
  - data/merged/comparison.csv → abrir en VS Code o Excel
    → Mostrar 5-10 filas, señalar diferencias de precio entre plataformas
  - data/screenshots/ → "Evidencia visual de cada extraccion"

DEMO REPORT: Abrir reports/insights.html en browser
  - Scroll rapido por las secciones
  - "Ahora vamos a profundizar en los insights..."
```

### 3. Datos Recolectados (3 min)

```
SLIDE 5: Cobertura de datos
  Tabla: Plataforma × Metricas obtenidas
  - Rappi: ✅ precios, ✅ fee, ✅ tiempo, ✅ promos, ✅ disponibilidad
  - Uber: ✅ precios, ✅ fee, ⚠️ tiempo (requiere dir), ⚠️ promos
  - DiDi: ⚠️/✅ (lo que se logro)
  
  Numero total de data points: XXX
  Success rate: XX%

SLIDE 6: Calidad de datos
  - "Verifique los datos manualmente vs la pagina real"
  - Screenshot de la plataforma al lado del dato extraido
  - Ejemplo: "Big Mac en Rappi muestra $155, mi scraper extrajo $155.00 ✅"

SLIDE 7: Distribucion por capa de recoleccion
  - Pie chart: X% API, Y% DOM, Z% Vision
  - "El sistema uso la capa mas eficiente en cada caso"
```

### 4. Top 5 Insights (10 min — la seccion mas importante)

```
SLIDE 8: Vista general
  "5 insights accionables, uno por cada dimension de analisis"

SLIDE 9: Insight #1 — Posicionamiento de Precios
  Chart: Barras comparativa de precios (el chart principal)
  Finding + Impacto + Recomendacion
  Ejemplo: "Rappi es 6.9% mas caro en Big Mac vs Uber Eats"
  2 min

SLIDE 10: Insight #2 — Ventaja Operacional
  Chart o dato sobre tiempos de entrega / cobertura
  Finding + Impacto + Recomendacion
  2 min

SLIDE 11: Insight #3 — Estructura de Fees
  Chart: comparativa de delivery fees
  "Rappi ofrece envio gratis como promo, Uber cobra $4.99 fijo"
  2 min

SLIDE 12: Insight #4 — Estrategia Promocional
  Datos sobre promociones detectadas
  "Rappi tiene 64% OFF y envio gratis. Uber no muestra promos visibles"
  2 min

SLIDE 13: Insight #5 — Variabilidad Geografica
  Chart: Heatmap de precios por zona
  "En periferia, las diferencias de precio se reducen a <2%"
  2 min
```

### 5. Decisiones Tecnicas (4 min)

```
SLIDE 14: Arquitectura de 3 capas
  Diagrama mermaid renderizado (de sistema-general.md)
  "Por que 3 capas: resiliencia, no depender de 1 sola tecnica"

SLIDE 15: Integracion de IA local
  "4 modelos de Ollama, cero costo de APIs externas"
  - qwen3-vl:8b → OCR de screenshots
  - qwen3.5:9b → Generacion de insights
  - nomic-embed-text → Matching de productos
  - qwen3.5:4b → Parseo de texto roto
  
  "El rol es AI Engineer. La IA no es un adorno, es parte del flujo critico"

SLIDE 16: Stack
  Python 3.10+ | Playwright | Ollama | pandas | matplotlib
  "Todo local, reproducible, un solo pip install"
```

### 6. Limitaciones y Next Steps (3 min)

```
SLIDE 17: Limitaciones honestas
  - Service fee no accesible sin simular compra (decision consciente, ADR-003)
  - DiDi Food cobertura parcial (documentado, no escondido)
  - Datos de 1 dia (no tendencia temporal)
  - Selectores CSS pueden cambiar

SLIDE 18: Next steps (si fuera produccion)
  - Scheduler diario (cron) para tracking temporal
  - Agregar ciudades: Monterrey, Guadalajara
  - API interna para consumo de otros equipos
  - Dashboard Streamlit para stakeholders
  - Alertas: "Uber bajo sus precios 10% en zona premium"

SLIDE 19: Cierre
  "Construi un sistema que garantiza datos aunque el scraping falle,
   normaliza con IA, y genera insights accionables automaticamente.
   Preguntas?"
```

### 7. Q&A (10 min)

```
PREGUNTAS PROBABLES Y RESPUESTAS:

P: "Que pasa si te bloquean?"
R: "Tengo 3 capas. Si Capa 1 y 2 fallan, la Capa 3 (screenshot + OCR) 
    siempre funciona. Ademas tengo datos pre-scrapeados como backup."

P: "Por que no usaste [herramienta X]?"
R: "Evalué 4 opciones en mi decision matrix (doc 06). Playwright gano
    por balance entre API interception, async, y comunidad."

P: "Como escalarias esto?"
R: "Scheduler diario, mas ciudades, API REST, alertas automaticas.
    La arquitectura de 3 capas escala horizontalmente."

P: "Por que Rappi primero y no Uber?"
R: "Hice un spike tecnico real (doc 09). Rappi tiene mejor accesibilidad
    web y es el baseline del caso."

P: "El service fee no lo tienes, eso es un problema?"
R: "Es una limitacion documentada (ADR-003). Requiere simular una compra,
    lo cual tiene riesgo de anti-fraude. Con acceso a APIs internas de Rappi,
    se resolveria en produccion. Tengo 5 de 7 metricas, 167% del minimo."

P: "Que modelo de IA usas y por que local?"
R: "Ollama con modelos Qwen y nomic. Local = cero costo, sin latencia de API,
    sin limites de rate, funciona offline. Para produccion se podria escalar
    a API cloud si se necesita."
```

---

## Materiales Necesarios

| Material | Estado | Generado por |
|----------|--------|-------------|
| Slides (Google Slides/PPT) | Crear en MVP 4 | Manual |
| reports/insights.html | Auto-generado | ReportGenerator |
| Charts en reports/charts/ | Auto-generados | Visualizations |
| Demo script (`--debug`) | Listo desde MVP 1 | CLI |
| Datos pre-scrapeados | Generar antes de la demo | `--save-backup` |
| Screenshots de evidencia | Auto-capturados | Capa 3 + screenshots config |
