<!-- AUTO-GENERATED: Do not edit directly. Edit AGENTS.md and run: bash skills/setup.sh --sync -->
<!-- Last synced: 2026-04-08T00:58:15Z -->

# Rappi Competitive Intelligence System - Agent Guidelines

## How to Use This Guide

- Start here for project norms. This is a single-repo project with distinct phases.
- Each phase has its own folder with a local `AGENTS.md` that overrides this file:
  - `Analisis/` → Fase de analisis y requerimientos
  - `diseno/` → Fase de diseno tecnico y arquitectura
  - `desarrollo/` → Fase de desarrollo, guias e implementacion
  - `pruebas/` → Fase de pruebas, QA y validacion
- Each phase also has skills in `skills/` with specific `SKILL.md` files.
- **Override priority**: Folder `AGENTS.md` > Skill `SKILL.md` > Root `AGENTS.md`
- **IMPORTANT**: Run `bash skills/setup.sh` to sync this file to `CLAUDE.md` for Claude Code compatibility.

---

## Available Skills

Use these skills for detailed patterns on-demand:

### Project Skills

| Skill | Description | URL |
|-------|-------------|-----|
| `analisis` | Fase de analisis y requerimientos | [SKILL.md](skills/analisis/SKILL.md) |
| `diseno` | Fase de diseno tecnico y arquitectura | [SKILL.md](skills/diseno/SKILL.md) |
| `desarrollo` | Fase de desarrollo e implementacion | [SKILL.md](skills/desarrollo/SKILL.md) |
| `scraping` | Patrones de scraping con Playwright/Nodriver | [SKILL.md](skills/scraping/SKILL.md) |
| `insights` | Generacion de insights y visualizaciones | [SKILL.md](skills/insights/SKILL.md) |
| `testing` | Estrategia y ejecucion de pruebas | [SKILL.md](skills/testing/SKILL.md) |
| `commit` | Conventional commits + versionamiento | [SKILL.md](skills/commit/SKILL.md) |
| `pr` | Convenciones de Pull Request | [SKILL.md](skills/pr/SKILL.md) |
| `gitflow` | Branching strategy y versionamiento | [SKILL.md](skills/gitflow/SKILL.md) |
| `skill-sync` | Sincroniza skills a AGENTS.md y CLAUDE.md | [SKILL.md](skills/skill-sync/SKILL.md) |
| `skill-creator` | Crear nuevas skills para el proyecto | [SKILL.md](skills/skill-creator/SKILL.md) |

### Auto-invoke Skills

When performing these actions, ALWAYS invoke the corresponding skill FIRST:

| Action | Skill |
|--------|-------|
| Analyzing requirements or business context | `analisis` |
| Creating architecture diagrams or technical design | `diseno` |
| Writing scraper code (Playwright, Nodriver, requests) | `scraping` |
| Implementing any Python module in src/ | `desarrollo` |
| Generating charts, reports or insights | `insights` |
| Writing or running tests | `testing` |
| Creating a git commit | `commit` |
| Creating a Pull Request | `pr` |
| Creating/merging branches or releasing versions | `gitflow` |
| After creating/modifying a skill | `skill-sync` |
| Creating new skills | `skill-creator` |
| Working with Playwright browser automation | `scraping` |
| Processing scraped data with pandas | `desarrollo` |
| Generating matplotlib/plotly visualizations | `insights` |
| Writing pytest tests | `testing` |
| Tagging a release version | `gitflow` |
| Fixing a bug | `testing` |
| Refactoring code | `desarrollo` |
| Working on files in diseno/ | `diseno` |
| Creating ADRs or architecture decisions | `diseno` |
| Working on files in desarrollo/ | `desarrollo` |
| Documenting scraping progress or technical notes | `desarrollo` |
| Working on files in pruebas/ | `testing` |
| Creating test cases or checklists | `testing` |
| Validating data quality | `testing` |
| Preparing for demo or presentation | `testing` |

---

## Project Overview

Sistema de Competitive Intelligence que recolecta datos de plataformas de delivery (Rappi, Uber Eats, DiDi Food) en Mexico para generar insights accionables.

| Fase | Location | Local AGENTS.md | Contenido |
|------|----------|-----------------|-----------|
| Analisis | `Analisis/` | - | Documentos de requerimientos y mercado |
| Diseno | `diseno/` | [AGENTS.md](diseno/AGENTS.md) | Arquitectura, ADRs, schemas, wireframes |
| Desarrollo | `desarrollo/` | [AGENTS.md](desarrollo/AGENTS.md) | **Todo el codigo**: src/, tests/, config/, data/, reports/ |
| Pruebas | `pruebas/` | [AGENTS.md](pruebas/AGENTS.md) | QA docs, casos de prueba, checklists, evidencia |
| Skills | `skills/` | - | AI agent skills (SKILL.md) |

### Desarrollo Tech Stack (inside desarrollo/)

| Component | Location | Tech Stack |
|-----------|----------|------------|
| Scrapers | `desarrollo/src/scrapers/` | Python 3.10+, Playwright, Nodriver |
| Models | `desarrollo/src/models/` | Python, Pydantic |
| Processors | `desarrollo/src/processors/` | Python, pandas |
| Analysis | `desarrollo/src/analysis/` | pandas, matplotlib, plotly |
| Utils | `desarrollo/src/utils/` | Python |
| Config | `desarrollo/config/` | JSON, YAML |
| Tests | `desarrollo/tests/` | pytest, pytest-asyncio |
| Data | `desarrollo/data/` | JSON (raw), CSV (merged) |
| Reports | `desarrollo/reports/` | HTML, Jupyter Notebooks |
| Notebooks | `desarrollo/notebooks/` | Jupyter |

## Project Structure

```
SistemaCompetitiveIntelligence/
├── AGENTS.md                    # THIS FILE - Agent guidelines
├── CLAUDE.md                    # Auto-generated from AGENTS.md (setup.sh)
├── README.md                    # Human documentation
├── Analisis/                    # Fase: Analisis y requerimientos
│   ├── 01-resumen-requerimiento.md
│   ├── 02-analisis-mercado.md
│   ├── 03-enfoques-solucion.md
│   ├── 04-mvp-roadmap.md
│   ├── 05-arquitectura-propuesta.md
│   └── 06-decision-matrix.md
├── diseno/                      # FASE: Diseno tecnico
│   ├── AGENTS.md                # Local agent guidelines
│   ├── arquitectura/            # Diagramas de arquitectura
│   ├── modelos/                 # Schemas y modelos de datos
│   ├── decisiones/              # ADRs (Architecture Decision Records)
│   └── dashboard/               # Wireframes dashboard
├── desarrollo/                  # FASE: Desarrollo (TODO el codigo aqui)
│   ├── AGENTS.md                # Local agent guidelines
│   ├── src/                     # Codigo fuente
│   │   ├── scrapers/            # Scrapers por plataforma
│   │   ├── models/              # Pydantic dataclasses
│   │   ├── processors/          # Normalizacion de datos
│   │   ├── analysis/            # Insights y visualizaciones
│   │   ├── utils/               # Helpers
│   │   ├── config.py            # Config loader
│   │   └── main.py              # CLI entry point
│   ├── config/                  # Configuracion
│   │   ├── addresses.json       # Direcciones a scrapear
│   │   ├── products.json        # Productos referencia
│   │   └── settings.yaml        # Settings generales
│   ├── tests/                   # Tests automatizados
│   │   ├── test_scrapers.py
│   │   ├── test_normalizer.py
│   │   └── test_models.py
│   ├── data/                    # Datos generados
│   │   ├── raw/                 # JSON por scraping run
│   │   ├── merged/              # CSV consolidado
│   │   └── screenshots/         # Capturas de pantalla
│   ├── reports/                 # Reportes generados
│   │   └── charts/              # Imagenes de graficos
│   ├── notebooks/               # Jupyter notebooks
│   ├── guias/                   # Guias de implementacion
│   ├── progreso/                # Logs de progreso por MVP
│   ├── notas-tecnicas/          # Endpoints, selectores, anti-bot
│   ├── troubleshooting/         # Problemas y soluciones
│   ├── requirements.txt         # Dependencias Python
│   └── .env.example             # Variables de entorno template
├── pruebas/                     # FASE: Pruebas y QA
│   ├── AGENTS.md                # Local agent guidelines
│   ├── casos/                   # Casos de prueba por componente
│   ├── reportes/                # Resultados de ejecucion
│   ├── evidencia/               # Screenshots, validacion manual
│   └── checklists/              # Pre-entrega, pre-demo
├── skills/                      # AI agent skills
│   ├── setup.sh                 # Sync AGENTS.md -> CLAUDE.md
│   └── {skill-name}/SKILL.md
└── .gitignore
```

---

## Python Development

All commands run from inside `desarrollo/`:

```bash
# Setup
cd desarrollo
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
playwright install chromium

# Run scraper
python -m src.main

# Run tests
pytest tests/ -v

# Lint
ruff check src/
ruff format src/
```

---

## Commit & Pull Request Guidelines

Follow conventional-commit style: `<type>(scope): <description>`

**Types:** `feat`, `fix`, `docs`, `chore`, `perf`, `refactor`, `style`, `test`

**Scopes:** `scraper`, `analysis`, `config`, `data`, `docs`, `ci`, `skills`

**Examples:**
```
feat(scraper): add Uber Eats price extraction for CDMX
fix(scraper): handle missing delivery fee in DiDi Food
docs: update README with setup instructions
chore(config): add 10 new addresses for Monterrey
test(scraper): add unit tests for data normalizer
```

Before creating a PR (run from `desarrollo/`):
1. Run all tests: `pytest tests/ -v`
2. Lint code: `ruff check src/`
3. Update CHANGELOG.md if applicable

---

## Branching Strategy (GitFlow)

```
main              ← Production-ready, tagged versions (v0.1.0, v0.2.0...)
├── develop       ← Integration branch, latest working code
│   ├── feature/  ← New features (feature/uber-eats-scraper)
│   ├── fix/      ← Bug fixes (fix/proxy-rotation)
│   └── docs/     ← Documentation (docs/readme-update)
├── release/      ← Release candidates (release/v0.1.0)
└── hotfix/       ← Emergency fixes on main (hotfix/critical-bug)
```

**Version Tagging:** Semantic Versioning `vMAJOR.MINOR.PATCH`
- `v0.1.0` - MVP 0+1: Single platform scraper working
- `v0.2.0` - MVP 2: Multi-platform scraping
- `v0.3.0` - MVP 3: Insights & visualizations
- `v0.4.0` - MVP 4: Polish & presentation ready
- `v1.0.0` - Complete deliverable

---

## Phases & MVPs

| Phase | MVP | Branch | Tag | Description |
|-------|-----|--------|-----|-------------|
| Analisis | - | `docs/analisis` | - | Requirements & market research |
| Diseno | - | `docs/diseno` | - | Architecture & technical design |
| Desarrollo | MVP 0 | `feature/poc-uber-eats` | `v0.1.0-alpha` | Proof of concept 1 platform |
| Desarrollo | MVP 1 | `feature/uber-eats-scraper` | `v0.1.0` | Single platform multi-address |
| Desarrollo | MVP 2 | `feature/multi-platform` | `v0.2.0` | 3 platforms integrated |
| Insights | MVP 3 | `feature/insights-report` | `v0.3.0` | Analysis + visualizations |
| Polish | MVP 4 | `release/v0.4.0` | `v0.4.0` | README + demo + presentation |
| Bonus | MVP 5 | `feature/dashboard` | `v0.5.0` | Streamlit dashboard |

---

## Rules for the AI Agent

1. **Read before writing**: Always read existing files before modifying them.
2. **Follow the phase**: Check which MVP/phase we're in before suggesting work.
3. **Invoke skills**: Use the Auto-invoke table to load relevant skills before acting.
4. **Commit discipline**: Never commit without user approval. Follow conventional commits.
5. **Branch discipline**: Work on the correct branch for the current phase.
6. **Test before merge**: Run tests before any merge to develop/main.
7. **Data safety**: Never commit .env files, API keys, or proxy credentials.
8. **Pragmatism**: Prefer simple solutions. Don't over-engineer.
9. **Document blockers**: If scraping fails, log the reason and continue.
10. **Spanish context**: Business insights and user communication in Spanish. Code and commits in English.
