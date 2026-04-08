# Checklist: MVP 3 — Insights + Reporte

**Fecha:** ____-__-__
**Branch:** feature/insights-report
**Tag:** v0.3.0

---

## Automatizados

- [ ] `pytest tests/ -v` pasa 100% (130 tests)
- [ ] `ruff check src/` sin errores

## Manuales

- [ ] `python -m src.main --report-only --report-data data/merged/comparison_combined.csv` genera reporte
- [ ] `reports/insights.html` se abre correctamente en browser
- [ ] 4 charts visibles en el HTML (barras, heatmap, scatter, tabla)
- [ ] 5 insights con formato: Finding, Impacto, Recomendacion
- [ ] Resumen ejecutivo presente y coherente
- [ ] Charts en reports/charts/ como PNG individuales

## Datos

- [ ] HTML es autocontenido (imagenes base64, no refs externas)
- [ ] Insights mencionan datos reales del CSV
- [ ] Colores de plataformas: Rappi naranja, Uber verde
