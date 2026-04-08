# Casos de Prueba — MVP 3: Insights + Reporte

**MVP:** 3
**Branch:** feature/insights-report
**Tag:** v0.3.0

---

## Caso: TC-301 — 5 insights generados con formato correcto

**Tipo:** Unitario (automatizado)

### Pasos
1. `pytest tests/test_insights.py -v`

### Resultado Esperado
- 5 insights, cada uno con number, title, dimension, finding, impact, recommendation
- Cada insight cubre 1 dimension diferente de las 5 del brief

---

## Caso: TC-302 — 4 charts se generan sin errores

**Tipo:** Unitario (automatizado)

### Pasos
1. `pytest tests/test_visualizations.py -v`

### Resultado Esperado
- price_comparison.png generado con barras por plataforma
- zone_heatmap.png generado
- fee_vs_time.png scatter generado
- price_table.html con tabla pivot

---

## Caso: TC-303 — HTML se abre en browser correctamente

**Tipo:** Unitario (automatizado) + Manual

### Pasos
1. `pytest tests/test_report.py -v`
2. Abrir `reports/insights.html` en browser

### Resultado Esperado
- HTML autocontenido (imagenes base64, CSS inline)
- Secciones: Header, Resumen, Datos, Charts, 5 Insights, Limitaciones, Metodologia

---

## Caso: TC-304 — --report-only funciona con datos existentes

**Tipo:** E2E (manual)

### Pasos
1. `python -m src.main --report-only --report-data data/merged/comparison_combined.csv`

### Resultado Esperado
- No ejecuta scraping
- Genera charts + insights + HTML desde CSV existente
- reports/insights.html se actualiza

---

## Caso: TC-305 — Insights usan datos reales del CSV

**Tipo:** Manual

### Pasos
1. Abrir reports/insights.html
2. Verificar que los numeros en insights coinciden con el CSV

### Resultado Esperado
- Precios, fees, tiempos mencionados en insights corresponden a datos reales
- No hay numeros inventados

---

## Caso: TC-306 — Charts tienen labels correctos

**Tipo:** Unitario (automatizado)

### Pasos
1. `pytest tests/test_visualizations.py -v`

### Resultado Esperado
- Chart de barras tiene titulo, ejes, leyenda
- Colores: Rappi naranja, Uber Eats verde

---

## Caso: TC-307 — Resumen ejecutivo <= 100 palabras

**Tipo:** Unitario (automatizado)

### Pasos
1. `pytest tests/test_insights.py::TestExecutiveSummary -v`

### Resultado Esperado
- Resumen no vacio, menciona numero de plataformas
