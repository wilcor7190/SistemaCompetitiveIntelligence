# Estructura del Reporte de Insights

## 1. Formato Principal: HTML (insights.html)

El reporte principal es un archivo HTML autocontenido (CSS inline, imagenes embebidas en base64) que se puede abrir en cualquier browser sin servidor.

### Estructura de Secciones

```
reports/insights.html
═══════════════════════

┌─────────────────────────────────────────────┐
│  HEADER                                      │
│  Logo conceptual + Titulo                    │
│  "Competitive Intelligence Report"           │
│  "Delivery Platforms — CDMX, Abril 2026"     │
│  Generado: {fecha} | Datos: {n} data points  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  RESUMEN EJECUTIVO (1 parrafo)               │
│  Generado por qwen3.5:9b                     │
│  Max 100 palabras, lo mas impactante primero │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  DATOS DEL SCRAPING                          │
│  ┌──────────────────────────────────────┐    │
│  │ Tabla: resumen de cobertura          │    │
│  │ Plataforma | Dirs | Exito | Layer    │    │
│  │ Rappi      | 25   | 92%   | API:15  │    │
│  │ Uber Eats  | 25   | 80%   | DOM:8   │    │
│  │ DiDi Food  | 25   | 48%   | OCR:12  │    │
│  └──────────────────────────────────────┘    │
│  Nota: data points totales, % exito, capas   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  CHART 1: Comparativa de Precios (BARRAS)    │
│  ┌──────────────────────────────────────┐    │
│  │  [Bar chart: precio por producto     │    │
│  │   agrupado por plataforma]           │    │
│  │                                      │    │
│  │  Big Mac:    Rappi ████ $155         │    │
│  │              Uber  ███ $145          │    │
│  │              DiDi  ███ $139          │    │
│  │  McNuggets:  Rappi ███ $145         │    │
│  │              Uber  ████ $155         │    │
│  │  ...                                 │    │
│  └──────────────────────────────────────┘    │
│  Caption: "Precios de productos de           │
│  referencia en McDonald's por plataforma"    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  TOP 5 INSIGHTS                              │
│                                              │
│  ### Insight #1: [Titulo]                    │
│  **Finding:** dato con numeros               │
│  **Impacto:** por que importa para Rappi     │
│  **Recomendacion:** accion concreta          │
│                                              │
│  ### Insight #2: ...                         │
│  ### Insight #3: ...                         │
│  ### Insight #4: ...                         │
│  ### Insight #5: ...                         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  CHART 2: Heatmap por Zona (HEATMAP)         │
│  ┌──────────────────────────────────────┐    │
│  │  [Heatmap: delta de precio Rappi     │    │
│  │   vs promedio competencia por zona]  │    │
│  │                                      │    │
│  │         centro premium resid perif   │    │
│  │ Big Mac  +6%    +8%   +4%   +2%    │    │
│  │ McNugg   -7%    -5%   -6%   -8%    │    │
│  │ Combo    +0%    +2%   -1%   +0%    │    │
│  │ ...                                  │    │
│  └──────────────────────────────────────┘    │
│  Caption: "Diferencia porcentual de precios  │
│  Rappi vs competencia por zona y producto"   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  CHART 3: Delivery Fee vs Tiempo (SCATTER)   │
│  ┌──────────────────────────────────────┐    │
│  │  [Scatter plot: X=delivery fee,      │    │
│  │   Y=delivery time, color=platform]   │    │
│  │                                      │    │
│  │  ● Rappi  ■ Uber Eats  ▲ DiDi      │    │
│  │  fee vs tiempo por direccion         │    │
│  └──────────────────────────────────────┘    │
│  Caption: "Relacion entre costo de envio     │
│  y tiempo de entrega por plataforma y zona"  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  TABLA RESUMEN (bonus, chart 4 si hay datos) │
│  ┌──────────────────────────────────────┐    │
│  │  Tabla pivot: producto × plataforma  │    │
│  │  con precios, coloreada por delta    │    │
│  │  verde = mas barato, rojo = mas caro │    │
│  └──────────────────────────────────────┘    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  LIMITACIONES Y NEXT STEPS                   │
│  - Service fee no accesible (ADR-003)        │
│  - DiDi Food cobertura parcial               │
│  - Datos de 1 dia (no tendencia temporal)    │
│  - Next: scheduler diario, mas ciudades      │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  METODOLOGIA                                 │
│  - Sistema de 3 capas (ADR-002)              │
│  - 25 direcciones en 5 zonas de CDMX         │
│  - 5 productos de referencia (McDonald's)    │
│  - Modelos Ollama locales: qwen3-vl, etc.    │
│  - Generado: {fecha}                         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  FOOTER                                      │
│  "Generated by Competitive Intelligence      │
│   System v0.1.0 — AI-assisted insights"      │
└─────────────────────────────────────────────┘
```

---

## 2. Visualizaciones Requeridas (minimo 3)

### Chart 1: Barras Comparativa de Precios (OBLIGATORIO)

```python
# matplotlib implementation sketch
def chart_price_comparison(df: pd.DataFrame, output_path: str):
    """Barras agrupadas: precio por producto, agrupado por plataforma."""
    pivot = df.pivot_table(
        values='price_mxn', 
        index='canonical_product', 
        columns='platform', 
        aggfunc='mean'
    )
    ax = pivot.plot(kind='bar', figsize=(12, 6), color=['#FF6B35', '#06C167', '#FC6B2D'])
    ax.set_title('Precio Promedio por Producto y Plataforma (MXN)')
    ax.set_ylabel('Precio (MXN)')
    ax.set_xlabel('Producto')
    ax.legend(title='Plataforma')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
```

- Colores sugeridos: Rappi `#FF6B35` (naranja), Uber Eats `#06C167` (verde), DiDi `#FC6B2D` (naranja-rojo)
- Siempre incluir leyenda y labels de valores sobre las barras

### Chart 2: Heatmap de Variabilidad por Zona (OBLIGATORIO)

```python
def chart_zone_heatmap(df: pd.DataFrame, output_path: str):
    """Heatmap: delta porcentual Rappi vs competencia, por zona y producto."""
    # Calcular delta: (precio_rappi - precio_promedio_competencia) / precio_promedio_competencia
    rappi = df[df.platform == 'rappi'].groupby(['zone_type', 'canonical_product']).price_mxn.mean()
    others = df[df.platform != 'rappi'].groupby(['zone_type', 'canonical_product']).price_mxn.mean()
    delta = ((rappi - others) / others * 100).unstack()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(delta, annot=True, fmt='.1f', cmap='RdYlGn_r', center=0, ax=ax)
    ax.set_title('Delta de Precio Rappi vs Competencia (%)\nRojo = Rappi mas caro, Verde = Rappi mas barato')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
```

- Rojo = Rappi mas caro (negativo para Rappi)
- Verde = Rappi mas barato (positivo para Rappi)
- Centro del colormap en 0%

### Chart 3: Scatter Fee vs Tiempo (OBLIGATORIO)

```python
def chart_fee_vs_time(df: pd.DataFrame, output_path: str):
    """Scatter: delivery fee (X) vs tiempo de entrega (Y), color por plataforma."""
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {'rappi': '#FF6B35', 'uber_eats': '#06C167', 'didi_food': '#FC6B2D'}
    
    for platform, group in df.groupby('platform'):
        ax.scatter(
            group.delivery_fee_mxn, 
            group.delivery_time_max,
            c=colors[platform], 
            label=platform, 
            alpha=0.6, 
            s=80
        )
    
    ax.set_xlabel('Delivery Fee (MXN)')
    ax.set_ylabel('Tiempo de Entrega (min)')
    ax.set_title('Delivery Fee vs Tiempo de Entrega por Plataforma')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
```

### Chart 4: Tabla Pivot (BONUS)

```python
def chart_price_table(df: pd.DataFrame, output_path: str):
    """Tabla HTML con colores: producto × plataforma con precios."""
    pivot = df.pivot_table(
        values='price_mxn',
        index='canonical_product',
        columns='platform',
        aggfunc='mean'
    ).round(2)
    
    # Agregar columna delta
    if 'rappi' in pivot.columns:
        others_mean = pivot.drop(columns='rappi', errors='ignore').mean(axis=1)
        pivot['Delta Rappi vs Competencia'] = ((pivot['rappi'] - others_mean) / others_mean * 100).round(1)
    
    # Exportar como HTML con estilos
    styled = pivot.style.background_gradient(cmap='RdYlGn_r', subset=['Delta Rappi vs Competencia'])
    styled.to_html(output_path)
```

---

## 3. Formato Secundario: Jupyter Notebook

Archivo: `notebooks/analysis.ipynb`

```
Celda 1: Setup y carga de datos
  - import pandas, matplotlib, plotly
  - df = pd.read_csv("../data/merged/comparison.csv")

Celda 2: Resumen de datos
  - df.shape, df.describe(), df.platform.value_counts()

Celda 3: Chart 1 (barras)
  - Reproducir chart de precios comparativos

Celda 4: Chart 2 (heatmap)
  - Reproducir heatmap de zonas

Celda 5: Chart 3 (scatter)
  - Reproducir scatter fee vs tiempo

Celda 6: Analisis adicional
  - Top diferencias de precio
  - Disponibilidad por zona
  - Estadisticas descriptivas

Celda 7: Insights (texto)
  - Los 5 insights pegados como markdown
```

El notebook es para reproducibilidad. El evaluador puede ejecutar cada celda y ver los graficos generarse.

---

## 4. Archivos de Salida

```
reports/
├── insights.html              # Reporte principal autocontenido
├── charts/
│   ├── price_comparison.png   # Chart 1: barras
│   ├── zone_heatmap.png       # Chart 2: heatmap
│   ├── fee_vs_time.png        # Chart 3: scatter
│   └── price_table.html       # Chart 4: tabla pivot (bonus)
└── executive_summary.txt      # Resumen de 1 parrafo (para copiar/pegar)

notebooks/
└── analysis.ipynb             # Notebook reproducible
```
