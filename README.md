# 🔍 Competitive Intelligence System

> **Sistema de inteligencia competitiva con IA que recolecta, normaliza y analiza precios de Rappi, Uber Eats y DiDi Food en CDMX — generando insights accionables al nivel de un VP de Strategy.**

[![Tests](https://img.shields.io/badge/tests-130%20passing-brightgreen)](desarrollo/tests/)
[![Version](https://img.shields.io/badge/version-v0.4.0-blue)](https://github.com/wilcor7190/SistemaCompetitiveIntelligence/releases/tag/v0.4.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![Claude](https://img.shields.io/badge/Claude-Opus%204.6-purple)](https://anthropic.com/)
[![Status](https://img.shields.io/badge/status-production%20ready-success)](https://github.com/wilcor7190/SistemaCompetitiveIntelligence)

---

## 🎯 30 segundos: ¿Qué hace?

Construí un sistema que **scrapea las 3 principales plataformas de delivery en México**, normaliza los datos con IA, y genera **5 insights accionables** con un resumen ejecutivo escrito por Claude Opus 4.6.

**Resultado real (verificado):**

```
📊 Big Mac Tocino:    $155 MXN (Rappi)  vs  $204 MXN (Uber Eats)  →  Rappi 32% más barato
📊 McNuggets 10 pzs:  $145 MXN (Rappi)  vs  $155 MXN (Uber Eats)  →  Rappi 6.9% más barato
📊 Coca-Cola 600ml:   $19 MXN  (Rappi)
📊 Delivery fee:      Gratis  (Rappi)   vs  Variable (Uber Eats)
📊 Tiempo entrega:    35 min  (Rappi)   vs  25-35 min (Uber Eats)
```

> 💡 **El resumen ejecutivo del reporte fue escrito por Claude Opus 4.6** con estos datos reales. Es indistinguible del de un analista senior.

---

## 🚀 Pruébalo en 2 minutos

```bash
# 1. Clonar
git clone https://github.com/wilcor7190/SistemaCompetitiveIntelligence.git
cd SistemaCompetitiveIntelligence/desarrollo

# 2. Setup (1 minuto)
python -m venv venv
source venv/Scripts/activate          # Windows Git Bash / Linux / macOS: source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 3. Configurar Claude API (opcional pero recomendado)
cp .env.example .env
# Editar .env y agregar: ANTHROPIC_API_KEY=sk-ant-...
# (Anthropic regala $5 USD al registrarse: https://console.anthropic.com/settings/keys)

# 4. ¡Demo! (Sin scraping en vivo, usa datos pre-scrapeados)
python -m src.main --use-backup

# 5. Abre el reporte
start reports/insights.html        # Windows
open reports/insights.html         # macOS
xdg-open reports/insights.html     # Linux
```

**Sin internet?** El modo `--use-backup` funciona offline con datos pre-verificados.
**Sin API key?** El sistema sigue funcionando con insights stats-based como fallback.

---

## ✨ Lo que demuestra este proyecto

### 1. Ingeniería defensiva: 3 capas de recolección

```
┌────────────────────────────────────────────────┐
│  Capa 1: API Interception                      │  ← Más rápido (intercepta APIs internas)
│  ↓ (si falla)                                  │
│  Capa 2: DOM Parsing                           │  ← Selectores CSS verificados con DevTools
│  ↓ (si falla)                                  │
│  Capa 3: Vision AI (Claude)                    │  ← Toma screenshot, Claude lo "lee"
└────────────────────────────────────────────────┘
```

**Si Rappi cambia su HTML mañana, el sistema NO se rompe.** Cae automáticamente a Capa 3 que lee la imagen del screenshot. **Resiliencia by design**, no por accidente.

### 2. IA en el lugar correcto

| Función | Modelo | Por qué |
|---------|--------|---------|
| **Resumen ejecutivo** | Claude Opus 4.6 | Calidad de analista senior, narrativa profesional |
| **Vision OCR (Capa 3)** | Claude Vision | Resiliencia anti-cambios de HTML |
| **Insights estadísticos** | pandas (sin LLM) | Determinístico, reproducible, sin costo |

> 💡 **No usé IA por usarla.** Cada componente tiene una razón específica documentada en [`diseno/decisiones/`](diseno/decisiones/).

### 3. Honestidad técnica

DiDi Food **no funciona** y lo digo claramente. El brief dice "priorizar calidad sobre cantidad" — preferí 2 plataformas con datos verificados que 3 a medias.

📄 Documentado en [`pruebas/casos/mvp2-multi-platform.md`](pruebas/casos/mvp2-multi-platform.md) y en la sección de limitaciones del reporte HTML.

---

## 📊 Datos reales verificados

| Producto | Rappi | Uber Eats | Diferencia |
|----------|------:|----------:|-----------:|
| Big Mac Tocino | **$155** | $204 | -32% |
| McNuggets 10 pzs | **$145** | $155 | -6.9% |
| Coca-Cola 600ml (Turbo) | **$19** | (Arkose) | N/A |
| Hamburguesa con Queso | **$59** | $79 | -25% |
| McFlurry Oreo | **$59** | (no scrapeado) | N/A |

| Métrica operacional | Rappi | Uber Eats |
|---------------------|-------|-----------|
| Delivery fee | **Gratis** | $5-$15 |
| Tiempo entrega | 35 min | 25-35 min |
| Rating | 4.1 ⭐ | 4.5+ ⭐ |
| Promociones activas | 100% obs | ~30% obs |

**Cobertura del scraping:**

| Plataforma | Status | Items extraídos |
|------------|--------|-----------------|
| **Rappi** | ✅ Production | 83 productos restaurant + 31 convenience |
| **Uber Eats** | ✅ Production | 33 productos restaurant |
| **DiDi Food** | ⚠️ Documentado | SPA vanilla sin SSR (limitación conocida) |

---

## 🏗️ Arquitectura

```
                    ┌──────────────────┐
                    │   CLI (main.py)  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────────┐
                    │  ScrapingOrchestrator │
                    │  + Circuit Breaker    │
                    └─┬─────────┬─────────┬┘
                      ↓         ↓         ↓
                ┌─────────┐┌────────┐┌─────────┐
                │  Rappi  ││UberEats││DiDi Food│
                └────┬────┘└───┬────┘└────┬────┘
                     │         │          │
                     ↓         ↓          ↓
                ┌──────────────────────────────┐
                │ BaseScraper (3 capas)        │
                │   API → DOM → Claude Vision  │
                └──────────────┬───────────────┘
                               ↓
                    ┌──────────────────┐
                    │  Normalizer +    │
                    │  Validator +     │
                    │  Merger          │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────────────┐
                    │  comparison.csv          │
                    └────────┬─────────────────┘
                             ↓
                    ┌──────────────────────────┐
                    │  InsightGenerator        │
                    │  + Claude Opus 4.6       │
                    │  + 4 charts (matplotlib) │
                    └────────┬─────────────────┘
                             ↓
                    ┌──────────────────────────┐
                    │  reports/insights.html   │  ← Reporte final
                    └──────────────────────────┘
```

**Stack:** Python 3.10+ | Playwright | Pydantic | pandas | matplotlib | seaborn | **Anthropic Claude API (Opus 4.6)** | aiohttp

---

## 🛡️ Pensado para fallar

| Escenario | Comportamiento del sistema |
|-----------|----------------------------|
| 🔴 Rappi cambia su HTML | Capa 2 falla → screenshot → Claude vision → continúa |
| 🔴 Uber Eats activa Arkose | Detecta → log warning → marca como fallido → continúa con otras dirs |
| 🔴 Sin internet | `--use-backup` carga datos pre-scrapeados → reporte normal |
| 🔴 Sin Claude API key | Insights stats-based con pandas → todo lo demás funciona |
| 🔴 60% de fallos en una plataforma | Circuit breaker la pausa, sigue con otras |
| 🔴 Datos corruptos | Pydantic los rechaza antes del CSV |

**En NINGÚN escenario me quedo sin datos para presentar.**

---

## 🧪 Calidad

```bash
cd desarrollo && pytest tests/ -v
```

```
============================== 130 passed in 7.2s ==============================
```

| Cobertura | Estado |
|-----------|--------|
| Modelos Pydantic | ✅ 22 tests |
| Config loader | ✅ 13 tests |
| Normalizer (precios, fees, tiempos) | ✅ 22 tests |
| Product matcher | ✅ 13 tests |
| CSV merger | ✅ 7 tests |
| Validator | ✅ 10 tests |
| Scrapers (factory, abstracción) | ✅ 11 tests |
| Integración (pipeline mock) | ✅ 9 tests |
| Insights | ✅ 9 tests |
| Visualizaciones | ✅ 7 tests |
| Reporte HTML | ✅ 7 tests |

**Linter:** `ruff check src/` → ✅ Clean

---

## 🎓 Decisiones técnicas (ADRs)

| ADR | Decisión | Por qué importa |
|-----|----------|-----------------|
| [ADR-001](diseno/decisiones/ADR-001-orden-plataformas.md) | Rappi primero | Mejor accesibilidad web → baseline confiable |
| [ADR-002](diseno/decisiones/ADR-002-tres-capas-recoleccion.md) | 3 capas con fallback | Resiliencia ante cambios anti-bot |
| [ADR-003](diseno/decisiones/ADR-003-service-fee-limitacion.md) | Service fee no accesible | Decisión consciente de no simular compra |
| [ADR-004](diseno/decisiones/ADR-004-estrategia-retail.md) | Estrategia retail multi-store | Restaurant + convenience + farmacia |
| [ADR-005](diseno/decisiones/ADR-005-migracion-ollama-a-claude.md) | **Migración Ollama → Claude API** | Velocidad 6-10x, calidad VP, setup trivial |

> 💡 **Lectura recomendada:** [ADR-005](diseno/decisiones/ADR-005-migracion-ollama-a-claude.md) — explica por qué cambié de Ollama local a Claude API durante MVP 4 después de descubrir problemas reales en producción. Demuestra que las decisiones de diseño deben validarse en la implementación.

---

## ⚠️ Limitaciones (honestas)

- **DiDi Food**: No produce datos. SPA vanilla sin SSR + posible login. Documentado como limitación. 2 plataformas con datos reales > 3 a medias.
- **Service fee**: No accesible sin simular compra (decisión documentada en ADR-003).
- **Convenience Uber Eats**: Bloqueado por Arkose anti-bot.
- **Capa 3 (Vision)**: Requiere `ANTHROPIC_API_KEY` (el sistema funciona sin ella, solo pierdes esa capa).

---

## 📚 Documentación completa

```
.
├── README.md                                  ← Estás aquí
├── Analisis/                                  ← Fase 1: Requerimientos y mercado
│   ├── 01-resumen-requerimiento.md
│   ├── 02-analisis-mercado.md
│   ├── 03-enfoques-solucion.md
│   ├── 04-mvp-roadmap.md
│   ├── 05-arquitectura-propuesta.md
│   ├── 06-decision-matrix.md
│   ├── 07-modelos-ollama-aplicacion.md
│   ├── 08-rumbo-estrategico.md
│   └── 09-reconocimiento-tecnico.md
├── diseno/                                    ← Fase 2: Arquitectura técnica
│   ├── arquitectura/   (sistema, flujos, prompts, navegación)
│   ├── decisiones/     (5 ADRs)
│   ├── modelos/        (schemas, normalización)
│   └── plan-mvps.md    (roadmap detallado)
├── desarrollo/                                ← Fase 3: Código
│   ├── src/            (~3500 líneas)
│   ├── tests/          (130 tests)
│   ├── config/         (settings, addresses, products)
│   ├── data/           (raw, merged, screenshots, backup)
│   ├── reports/        (insights.html + charts)
│   └── guias/          (cómo extender el sistema)
└── pruebas/                                   ← Fase 4: QA
    ├── casos/          (TC-001 a TC-307)
    ├── checklists/     (pre-entrega, pre-demo, por MVP)
    ├── reportes/       (resultados + auditoría técnica)
    ├── guia-presentacion.md          ← Script para la presentación
    └── informe-auditoria-final.md    ← Auditoría completa MVP 4
```

---

## 🎬 Comandos útiles

```bash
# Demo rápido (1 dirección, browser visible, ~30s)
python -m src.main --debug

# Modo backup (sin internet, usa datos pre-scrapeados)
python -m src.main --use-backup

# Solo regenerar reporte desde CSV existente
python -m src.main --report-only --report-data data/merged/comparison_combined.csv

# Scraping completo (25 direcciones × 2 plataformas, ~30 min)
python -m src.main --platforms rappi,uber_eats --headless

# Ver plan sin ejecutar
python -m src.main --dry-run

# Tests
pytest tests/ -v

# Lint
ruff check src/
```

📖 **Todos los flags:** [`pruebas/guia-presentacion.md`](pruebas/guia-presentacion.md) sección "Comandos"

---

## 🛠️ Extender el sistema

¿Quieres agregar otra sucursal, producto o plataforma? Tengo guía paso a paso:

📄 [`desarrollo/guias/como-agregar-tienda-o-plataforma.md`](desarrollo/guias/como-agregar-tienda-o-plataforma.md)

**Resumen:**

| Quiero... | Modificar | Tiempo |
|-----------|-----------|--------|
| Nueva dirección | `config/addresses.json` | 2 min |
| Nuevo producto | `config/products.json` | 2 min |
| Cambiar Claude → Haiku (ahorrar 80%) | `claude_client.py:14` | 1 min |
| Nueva plataforma (Pedidos Ya) | Crear scraper + registrar | 4-8 horas |

---

## 📈 Métricas del proyecto

| Métrica | Valor |
|---------|-------|
| Líneas de código Python | ~3,500 |
| Tests automatizados | **130** (100% passing) |
| MVPs entregados | **5** (v0.1.0-alpha → v0.4.0) |
| Tiempo de desarrollo | 5 fases incrementales |
| Plataformas funcionales | 2/3 (con datos reales verificados) |
| Costo por ejecución | ~$0.02-$0.05 USD (Claude API) |
| Tiempo demo `--debug` | ~30 segundos |
| Tiempo report-only | ~10 segundos |

---

## 🎯 ¿Por qué este proyecto vale la pena?

Para el rol de **AI Engineer** en Rappi, este proyecto demuestra:

✅ **Pensamiento de sistemas, no de scripts** — 3 capas con fallback, circuit breaker, resiliencia
✅ **IA como herramienta, no como adorno** — Claude se usa solo donde aporta valor real
✅ **Decisiones técnicas validadas** — Migración Ollama → Claude documentada en ADR-005
✅ **Calidad de código profesional** — 130 tests, ruff clean, type hints, async/await
✅ **Documentación honesta** — Limitaciones explícitas, no escondidas
✅ **Pensado para producción** — Logging, métricas, backups, observabilidad
✅ **Comunicación clara** — README, ADRs, guías, casos de prueba, presentación lista

**Y lo más importante:** todo está corriendo en GitHub. Puedes clonar y validarlo en 2 minutos.

---

## 📞 Contacto

**Repo:** https://github.com/wilcor7190/SistemaCompetitiveIntelligence
**Release:** [v0.4.0](https://github.com/wilcor7190/SistemaCompetitiveIntelligence/releases/tag/v0.4.0)

---

## 📝 Licencia

Proyecto de evaluación técnica para Rappi. No distribuir.

---

<div align="center">

**Construido con ❤️ y mucho café para el caso técnico de AI Engineer en Rappi**

*Si tienes preguntas, lee primero [`pruebas/guia-presentacion.md`](pruebas/guia-presentacion.md) — tiene 9 preguntas pre-respondidas.*

</div>
