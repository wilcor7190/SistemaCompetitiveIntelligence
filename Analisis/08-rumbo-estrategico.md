# 08 - Rumbo Estrategico: Como Abordar la Solucion

## El Problema Real (no el que parece)

Leido literalmente, el caso pide un scraper. Pero el caso **realmente** evalua esto:

```
"Tu mision es construir un sistema automatizado que recolecte datos
de la competencia y genere insights accionables para la toma de
decisiones estrategicas."
```

No dice "scrapea HTML". Dice **sistema automatizado** + **insights accionables**.

Y el rol es **AI Engineer**, no Web Scraper.

---

## Lo que ya sabemos (sintesis del analisis)

| Hallazgo | Documento | Implicacion |
|----------|-----------|-------------|
| No hay solucion off-the-shelf | 02-analisis-mercado | Hay que construir custom |
| No hay scrapers para Rappi/DiDi en Apify | 02-analisis-mercado | Al menos 2 de 3 plataformas son 100% custom |
| Anti-bot en 2026 es agresivo | 02-analisis-mercado | Scraping puede fallar, necesitamos Plan B |
| Enfoque hibrido (browser + API) es el mejor balance | 03-enfoques | No apostar todo a una sola tecnica |
| El scraping es 70% del peso pero tambien 90% del riesgo | 04-mvp-roadmap | Si falla el scraping, falla todo |
| Ollama con vision puede ser Plan B | 07-modelos-ollama | Screenshots + OCR = datos garantizados |
| LLM local puede generar insights | 07-modelos-ollama | Diferenciador como AI Engineer |

---

## La Tension Central

```
        RIESGO ALTO                          PESO ALTO
    ┌─────────────────┐               ┌─────────────────┐
    │   SCRAPING       │               │   SCRAPING       │
    │   Anti-bot       │               │   50% evaluacion │
    │   DOM cambia     │               │   70% entregable │
    │   Puede fallar   │               │                  │
    └────────┬────────┘               └────────┬────────┘
             │                                  │
             │      ¿Como obtener datos         │
             │      de forma CONFIABLE?         │
             │                                  │
             └──────────────┬───────────────────┘
                            │
                            v
              ┌─────────────────────────┐
              │  ESTRATEGIA MULTI-CAPA  │
              │  No depender de 1 sola  │
              │  fuente de datos        │
              └─────────────────────────┘
```

El scraping clasico es fragil. Un dia funciona, al otro dia Cloudflare lo bloquea. El brief lo sabe:

> "¿Que pasa si me bloquean durante el scraping? Es parte del desafio."

La respuesta no es "mejor scraper". La respuesta es **multiples formas de obtener datos**.

---

## Rumbo: Sistema de 3 Capas de Recoleccion

En vez de un scraper que puede fallar, construimos **3 capas de recoleccion**. Si una falla, la siguiente toma el control. Esto convierte el riesgo en una fortaleza.

```
CAPA 1: API Interception (la mas rapida y estable)
=========================================================
Playwright navega la web → intercepta network requests
→ descubre endpoints API internos → llama directo con requests
→ JSON limpio, rapido, estable

  Probabilidad de exito: ~60%
  Si funciona: es la mejor opcion (rapido, limpio, estable)
  Si falla: los endpoints requieren auth compleja → Capa 2


CAPA 2: Browser Automation + DOM Parsing (la clasica)
=========================================================
Playwright/Nodriver → navega como usuario real
→ espera que cargue → extrae del DOM con selectores CSS
→ parsea HTML → JSON

  Probabilidad de exito: ~70%
  Si funciona: datos completos del DOM
  Si falla: anti-bot bloquea o DOM cambio → Capa 3


CAPA 3: Screenshot + Vision AI (el Plan B inteligente)
=========================================================
Playwright → captura screenshot de la pagina
→ qwen3-vl:8b (Ollama local) → OCR inteligente → JSON

  Probabilidad de exito: ~95%
  Si funciona: datos extraidos de imagen, siempre funciona
  Limitacion: mas lento, posible perdida de precision en numeros

  EXTRA: Las screenshots quedan como EVIDENCIA
  (bonus del brief: "capturas automaticas de pantalla")
```

### Por que 3 capas y no solo 1

| Escenario | Solo scraper clasico | Sistema 3 capas |
|-----------|---------------------|-----------------|
| API descubierta | No la usa | Capa 1: rapido y limpio |
| DOM normal | Funciona | Capa 2: funciona igual |
| Anti-bot bloquea | **FALLA** | Capa 3: screenshot + OCR |
| Selector CSS roto | **FALLA** | Capa 3: screenshot + OCR |
| Demo en vivo falla | **Panico** | Capa 3 + datos pre-scrapeados |
| Evaluador pregunta "y si falla?" | "Pues... retry" | "Tengo 3 capas + datos backup" |

---

## Donde Entra la IA (y donde NO)

### SI usar IA

| Donde | Modelo | Justificacion |
|-------|--------|---------------|
| Capa 3: OCR de screenshots | `qwen3-vl:8b` | Plan B confiable, demuestra AI skills |
| Generacion de insights | `qwen3.5:9b` | Asistir en los 5 insights accionables |
| Matching de productos | `nomic-embed-text` | "Big Mac" vs "BigMac Individual" = same? |
| Parseo de texto roto | `qwen3.5:4b` | Fallback cuando selectores CSS fallan |

### NO usar IA (overengineering)

| Donde | Por que NO |
|-------|-----------|
| Orquestar scrapers con agente LLM | Un script Python con if/else es mas confiable en 2 dias |
| Decidir que direcciones scrapear | Es decision de negocio, no de IA |
| Generar el codigo del scraper | Ya lo estamos haciendo con Claude como herramienta |
| Analisis estadistico basico | pandas es mas preciso que un LLM para calcular promedios |

---

## Orden de Ataque (Critical Path)

Lo que determina el exito o fracaso del proyecto, en orden:

```
PRIORIDAD 1: ¿PUEDO OBTENER DATOS? (Dia 1 manana)
════════════════════════════════════════════════════
│
├─ Abrir ubereats.com con Playwright
├─ Abrir rappi.com.mx con Playwright
├─ Abrir didi-food.com con Playwright
│
├─ ¿Puedo interceptar APIs? → Si: usar Capa 1
├─ ¿Puedo parsear DOM? → Si: usar Capa 2
├─ ¿Me bloquean? → Screenshot + qwen3-vl → Capa 3
│
└─ RESULTADO: Se que funciona para cada plataforma
             Tengo al menos 1 dato real de cada una

PRIORIDAD 2: ESCALAR A 20+ DIRECCIONES (Dia 1 tarde)
════════════════════════════════════════════════════
│
├─ Definir 25 direcciones en 5 zonas de CDMX
├─ Loop por cada direccion × cada plataforma
├─ Rate limiting: 3-7s entre requests
├─ Guardar JSON por plataforma
│
└─ RESULTADO: Dataset crudo de ~225 data points
             (25 dirs × 3 plataformas × 3 productos)

PRIORIDAD 3: NORMALIZAR Y CONSOLIDAR (Dia 2 manana)
════════════════════════════════════════════════════
│
├─ Matching de productos con embeddings
├─ Normalizar schema entre plataformas
├─ Merge a CSV consolidado
├─ Validar datos: ¿hay gaps? → Completar con Capa 3
│
└─ RESULTADO: comparison.csv listo para analisis

PRIORIDAD 4: INSIGHTS CON IA (Dia 2 mediadia)
════════════════════════════════════════════════════
│
├─ Analisis con pandas (promedios, comparativas)
├─ qwen3.5:9b genera draft de 5 insights
├─ TU revisas, editas, ajustas (eres el gestor)
├─ 3+ visualizaciones con matplotlib
│
└─ RESULTADO: Informe con 5 insights accionables

PRIORIDAD 5: PRESENTACION (Dia 2 tarde)
════════════════════════════════════════════════════
│
├─ README con instrucciones
├─ Datos pre-scrapeados como backup
├─ Estructura de presentacion de 30 min
├─ Demo lista (o grabacion)
│
└─ RESULTADO: Listo para presentar
```

---

## Que Presentar y Como Contarlo

La narrativa de la presentacion no es "hice un scraper". Es:

> "Construi un **sistema de inteligencia competitiva con IA** que tiene 3 capas
> de recoleccion de datos. Si la capa principal falla, el sistema se adapta
> automaticamente. Los datos se normalizan con embeddings semanticos y los
> insights se generan asistidos por un LLM local. Todo corre sin APIs
> externas, cero costo operativo."

Eso es lo que dice un AI Engineer.

---

## Riesgos y Decision de Corte

| Si al final del Dia 1... | Que hacer |
|---------------------------|-----------|
| Tengo datos de 3 plataformas | Seguir plan normal |
| Tengo datos de 2 plataformas | Documentar la tercera como "blocker", seguir con 2 |
| Tengo datos de 1 plataforma | Agregar Capa 3 (OCR) para las otras 2, seguir |
| No tengo datos de ninguna | Capa 3 full (screenshots manuales + OCR) + documentar |

**No hay escenario donde llegues sin datos.** Ese es el punto del sistema de 3 capas.

---

## Decision: Que Enfoque Tomar

Basado en todo el analisis:

```
DECISION FINAL
═══════════════

Enfoque: C (Hibrido) + IA Local (Ollama)
  → Browser automation + API interception + Vision AI fallback

Stack:
  → Playwright (Python) como motor principal
  → Ollama (qwen3-vl:8b, qwen3.5:9b, nomic-embed-text) como IA
  → pandas + matplotlib para analisis
  → JSON + CSV para datos

Scope:
  → 3 plataformas: Uber Eats + Rappi + DiDi Food
  → 25 direcciones en CDMX (5 zonas × 5 dirs)
  → 5 productos referencia (3 fast food + 2 retail)
  → ~375 data points objetivo

Diferenciador:
  → Sistema de 3 capas (no solo scraping)
  → IA local para OCR, insights, matching
  → Cero costo de APIs externas
  → Resiliencia: siempre hay datos
```

---

## Siguiente Paso

Este documento cierra la fase de analisis. Los 8 documentos cubren:

```
01 - Que nos piden
02 - Que existe en el mercado
03 - Que opciones tenemos
04 - Como segmentar en MVPs
05 - Como se ve la arquitectura
06 - Que tecnologias elegir
07 - Que modelos de IA usar
08 - Que rumbo tomar (ESTE)
```

Cuando estes listo, pasamos a `diseno/` para detallar la arquitectura
con las 3 capas y la integracion de Ollama.
