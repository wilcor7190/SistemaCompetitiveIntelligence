# Checklist Pre-Entrega — MVP 4

**Fecha:** ____-__-__
**Tag:** v0.4.0
**Repo:** https://github.com/wilcor7190/SistemaCompetitiveIntelligence

---

## Quick Start funcional

- [ ] `git clone https://github.com/wilcor7190/SistemaCompetitiveIntelligence.git` funciona
- [ ] `cd desarrollo && python -m venv venv` funciona
- [ ] `source venv/Scripts/activate` (Windows) o `source venv/bin/activate` (Mac/Linux)
- [ ] `pip install -r requirements.txt` instala todas las dependencias sin errores
- [ ] `playwright install chromium` descarga el browser
- [ ] `python -m src.main --debug` ejecuta sin crash y extrae datos reales

## Tests y calidad

- [ ] `pytest tests/ -v` pasa 100% (130 tests)
- [ ] `ruff check src/` sin errores
- [ ] `ruff format src/ --check` sin diferencias

## Funcionalidad

- [ ] `python -m src.main --use-backup` genera reporte sin scraping en vivo
- [ ] `reports/insights.html` se abre en browser
- [ ] HTML tiene 5 insights + 4 charts visibles
- [ ] Charts: barras, heatmap, scatter, tabla
- [ ] CSV tiene datos de >=2 plataformas

## Datos pre-scrapeados

- [ ] `data/backup/` tiene archivos JSON validos
- [ ] `data/backup/comparison_backup_*.csv` existe
- [ ] `--use-backup` funciona con esos datos

## Documentacion

- [ ] README.md tiene Quick Start funcional copiar/pegar
- [ ] README incluye prerrequisitos (Python, Git, Playwright)
- [ ] README explica los flags principales del CLI
- [ ] `pruebas/` tiene casos de prueba y checklists por MVP
- [ ] `diseno/` tiene arquitectura y ADRs
- [ ] `Analisis/` tiene requerimientos

## Seguridad

- [ ] No hay `.env` en el repo
- [ ] No hay API keys en codigo
- [ ] `.gitignore` excluye `data/raw/`, `data/merged/`, `data/screenshots/`, `logs/`

## Git

- [ ] Branch `develop` actualizado
- [ ] Branch `main` actualizado con merge de develop
- [ ] Tag `v0.4.0` creado y pusheado
- [ ] GitHub Release `v0.4.0` publicado
