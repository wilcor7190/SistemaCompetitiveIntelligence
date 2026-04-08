---
name: insights
description: >
  Generacion de insights competitivos y visualizaciones.
  Trigger: Cuando se crean graficos, se analizan datos scrapeados,
  se generan reportes, o se trabaja en src/analysis/.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Generating charts, reports or insights"
    - "Generating matplotlib/plotly visualizations"
    - "Analyzing scraped data for business insights"
    - "Working on notebooks/ or reports/"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

## When to Use

1. Analyzing scraped data to generate business insights
2. Creating visualizations (charts, heatmaps, tables)
3. Building the final report or dashboard

## Critical Patterns

### Insight Format (Non-negotiable)
Every insight follows this template:
```markdown
### Insight #N: [Descriptive Title]

**Finding:** [Data-backed discovery with specific numbers]

**Impacto:** [Why it matters for Rappi - quantify if possible]

**Recomendacion:** [Concrete action Rappi should take]

**Evidencia:** [Reference to chart/table that supports this]
```

### Required Visualizations (Minimum 3)
1. **Bar chart**: Average price comparison per platform (products)
2. **Stacked bar**: Price breakdown (product + delivery fee + service fee)
3. **Heatmap or grouped bar**: Competitiveness by geographic zone

### Chart Style
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Consistent style for all charts
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {
    'rappi': '#FF441F',      # Rappi orange-red
    'uber_eats': '#06C167',  # Uber Eats green
    'didi_food': '#FF8C00',  # DiDi Food orange
}
```

### Analysis Dimensions (5 required)
1. Posicionamiento de precios (cheaper/similar/more expensive)
2. Ventaja/desventaja operacional (delivery times)
3. Estructura de fees (delivery + service fees)
4. Estrategia promocional (discounts, coupons)
5. Variabilidad geografica (differences by zone)

## Decision Tree

- Have scraped data in `desarrollo/data/merged/`?
  → YES: Load CSV and start analysis
  → NO: Run scraper first or use backup data
- Creating a new chart?
  → Use consistent COLORS dict and style
  → Save to `desarrollo/reports/charts/` as PNG
- Writing the final report?
  → Use Jupyter notebook, export to HTML
  → Ensure minimum 5 insights + 3 visualizations

## Commands

```bash
# Generate report from existing data (from desarrollo/)
cd desarrollo
python -m src.main --report-only --data data/merged/latest.csv

# Run Jupyter notebook
jupyter notebook notebooks/analysis.ipynb

# Export notebook to HTML
jupyter nbconvert --to html notebooks/analysis.ipynb --output ../reports/insights_report.html
```
