# Fase: Pruebas y Calidad

> Este archivo guia al agente cuando trabaja dentro de `pruebas/`.
> Overrides sobre el AGENTS.md raiz para esta fase.

## Proposito de esta carpeta

Contiene la **documentacion de calidad** del proyecto: casos de prueba, checklists, reportes de ejecucion y evidencia. Los **tests automatizados** viven en `desarrollo/tests/` (pytest); aqui vive la documentacion que acompana cada MVP.

## Estrategia de Pruebas por MVP

Cada MVP genera 3 artefactos en esta carpeta:

| Artefacto | Ubicacion | Cuando |
|-----------|-----------|--------|
| Casos de prueba | `casos/mvpN-xxx.md` | Al implementar el MVP |
| Checklist | `checklists/mvpN-checklist.md` | Antes de merge a develop |
| Reporte resultado | `reportes/mvpN-resultado.md` | Despues de ejecutar tests |

### Relacion tests automatizados ↔ documentacion pruebas

```
desarrollo/tests/          ← Codigo pytest (automatizado)
  test_models.py             Se ejecuta con: pytest tests/ -v
  test_normalizer.py         Resultado: PASS/FAIL en terminal
  ...

pruebas/                   ← Documentacion de QA (manual + evidencia)
  casos/mvp0-poc-rappi.md    Describe QUE se prueba y POR QUE
  checklists/mvp0-checklist.md  Lista de verificacion pre-release
  reportes/mvp0-resultado.md    Registro de QUE PASO al ejecutar
  evidencia/                    Screenshots, comparaciones manuales
```

**Regla:** Un MVP no se mergea a develop sin:
1. `pytest tests/ -v` pasa 100%
2. Checklist del MVP completado en `checklists/`
3. Reporte de resultado llenado en `reportes/`

## Que Probar por MVP

### MVP 0: PoC Rappi

| Test | Tipo | Donde | Automatizado |
|------|------|-------|-------------|
| Pydantic schemas crean instancias validas | Unitario | `tests/test_models.py` | Si |
| Config carga 3 archivos | Unitario | `tests/test_config.py` | Si |
| RappiScraper navega y extrae 1 dato | E2E | Manual | No |
| CLI --debug ejecuta sin crash | E2E | Manual | No |

### MVP 1: Rappi Completo

| Test | Tipo | Donde | Automatizado |
|------|------|-------|-------------|
| Parseo precios ($145, Gratis, rango) | Unitario | `tests/test_normalizer.py` | Si |
| Product matching por alias | Unitario | `tests/test_product_matcher.py` | Si |
| CSV tiene columnas correctas | Unitario | `tests/test_merger.py` | Si |
| Validacion rangos precios/fees | Unitario | `tests/test_validator.py` | Si |
| 25 dirs × Rappi sin crash | E2E | Manual | No |
| Multi-store (McDonald's + Oxxo) | E2E | Manual | No |
| Success rate ≥70% | Metrica | `reportes/mvp1-resultado.md` | No |

### MVP 2: Multi-Platform

| Test | Tipo | Donde | Automatizado |
|------|------|-------|-------------|
| Scraper factory crea scraper correcto | Unitario | `tests/test_scrapers.py` | Si |
| Pipeline mock: scrape → normalize → CSV | Integracion | `tests/test_integration.py` | Si |
| Deduplicacion funciona | Integracion | `tests/test_integration.py` | Si |
| Uber Eats extrae datos | E2E | Manual | No |
| DiDi Food extrae datos (o documenta fallo) | E2E | Manual | No |
| Datos comparables entre plataformas | Manual | `evidencia/comparacion-manual.md` | No |

### MVP 3: Insights + Reporte

| Test | Tipo | Donde | Automatizado |
|------|------|-------|-------------|
| Prompt tiene 5 dimensiones del brief | Unitario | `tests/test_insights.py` | Si |
| Charts se generan como PNG | Unitario | `tests/test_visualizations.py` | Si |
| HTML contiene secciones esperadas | Unitario | `tests/test_report.py` | Si |
| 5 insights con formato correcto | Manual | Revisar output | No |
| --report-only funciona | E2E | Manual | No |

### MVP 4: Pre-entrega

| Test | Tipo | Donde | Automatizado |
|------|------|-------|-------------|
| git clone + setup + --debug funciona | E2E | `checklists/pre-entrega.md` | No |
| pytest pasa 100% | Suite | Terminal | Si |
| ruff sin errores | Lint | Terminal | Si |
| --use-backup genera reporte | E2E | `checklists/pre-demo.md` | No |

## Estructura

```
pruebas/
├── AGENTS.md                    # THIS FILE
│
├── casos/                       # Casos de prueba por MVP
│   ├── mvp0-poc-rappi.md        # TC-001 a TC-004
│   ├── mvp1-rappi-completo.md   # TC-101 a TC-108
│   ├── mvp2-multi-platform.md   # TC-201 a TC-206
│   └── mvp3-insights.md         # TC-301 a TC-307
│
├── checklists/                  # Verificacion pre-release por MVP
│   ├── mvp0-checklist.md
│   ├── mvp1-checklist.md
│   ├── mvp2-checklist.md
│   ├── mvp3-checklist.md
│   ├── pre-entrega.md           # Checklist final (MVP 4)
│   └── pre-demo.md              # Checklist dia de la presentacion
│
├── reportes/                    # Resultados de ejecucion
│   ├── mvp0-resultado.md
│   ├── mvp1-resultado.md
│   ├── mvp2-resultado.md
│   ├── mvp3-resultado.md
│   └── mvp4-final.md            # Reporte final de calidad
│
└── evidencia/                   # Validacion manual
    ├── comparacion-manual.md    # Datos CSV vs pagina real (MVP 2)
    └── screenshots/             # Capturas de validacion
```

## Convenciones

### Nombres de archivos
- Kebab-case: `mvp0-poc-rappi.md`, `pre-entrega.md`
- Prefijo MVP: `mvp{N}-{nombre}.md`

### Formato de Caso de Prueba

```markdown
# Caso: TC-NNN — Titulo

**MVP:** 0 | 1 | 2 | 3 | 4
**Componente:** Models | Config | Scraper | Normalizer | Matcher | Merger | Insights | Report
**Prioridad:** Alta | Media | Baja
**Tipo:** Unitario | Integracion | E2E | Manual

## Precondiciones
[Que debe estar listo]

## Pasos
1. [Paso]
2. [Paso]

## Resultado Esperado
[Que deberia pasar]

## Resultado Real
[Llenar al ejecutar]

## Estado
Pasado | Fallido | Bloqueado | No ejecutado
```

### Formato de Checklist

```markdown
# Checklist: MVP N — Nombre

**Fecha:** YYYY-MM-DD
**Branch:** feature/xxx
**Tag:** vX.Y.Z

## Automatizados
- [ ] pytest tests/ -v pasa 100%
- [ ] ruff check src/ sin errores

## Manuales
- [ ] python -m src.main --debug ejecuta OK
- [ ] [verificaciones especificas del MVP]

## Datos
- [ ] Output tiene formato esperado
- [ ] Success rate >= umbral

## Seguridad
- [ ] No hay secrets en el codigo
- [ ] .env no esta en git
```

## Como Ejecutar las Pruebas

```bash
# Tests automatizados (desde desarrollo/)
cd desarrollo
source venv/Scripts/activate
pytest tests/ -v                    # Todos los tests
pytest tests/ -v --tb=short         # Output corto
pytest tests/test_models.py -v      # Solo un archivo
pytest tests/ -v -k "normalizer"    # Solo tests que matcheen

# Cobertura
pytest tests/ --cov=src --cov-report=html

# Lint
ruff check src/
ruff format src/ --check

# Verificacion E2E manual
python -m src.main --debug          # PoC rapido
python -m src.main --dry-run        # Plan sin ejecutar
python -m src.main --use-backup     # Con datos pre-scrapeados
```

## Skill asociado
Invoke `testing` skill cuando trabajes en esta carpeta.

## Relacion con otras carpetas
- **desarrollo/tests/** → Tests automatizados pytest (codigo)
- **desarrollo/data/** → Datos a validar (JSON, CSV, screenshots)
- **desarrollo/reports/** → Reportes a verificar (HTML, charts)
- **diseno/guia-ejecucion-mvps.md** → Prompts de tests por MVP
- **diseno/plan-mvps.md** → Criterios de exito por MVP
