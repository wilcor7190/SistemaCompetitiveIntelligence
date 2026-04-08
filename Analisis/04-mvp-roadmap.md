# 04 - MVP Roadmap: Plan Incremental de Entregas

## Filosofia: Empezar Simple, Iterar Rapido

> "Un producto en 3 direcciones bien comparado > 10 productos superficialmente"  
> -- Del brief del caso tecnico

Cada MVP es **funcional por si solo** y agrega valor al anterior. Si el tiempo se acaba en cualquier MVP, tienes algo entregable.

---

## MVP 0: Prueba de Concepto (2-4 horas)

### Objetivo
Validar que podemos extraer datos de AL MENOS 1 plataforma en 1 direccion.

### Scope
| Elemento | Valor |
|----------|-------|
| Plataformas | 1 (Uber Eats - mas documentada) |
| Direcciones | 1 (zona centrica CDMX) |
| Productos | 1 (Big Mac o equivalente) |
| Metricas | Precio + Delivery Fee |
| Output | Print en consola |

### Tareas
1. Abrir ubereats.com con Playwright
2. Setear una direccion (coordenadas o texto)
3. Buscar McDonald's
4. Extraer precio de Big Mac + delivery fee
5. Imprimir resultado

### Criterio de exito
```
{
  "platform": "uber_eats",
  "address": "Av. Reforma 222, CDMX",
  "restaurant": "McDonald's",
  "product": "Big Mac",
  "price": 89.00,
  "delivery_fee": 29.00,
  "timestamp": "2026-04-06T10:30:00"
}
```

### Riesgo principal
Anti-bot de Uber Eats bloquea el scraping inicial.

### Mitigacion
Si falla: probar con API interception (Network tab analysis).

---

## MVP 1: Scraper Single-Platform Multi-Address (4-6 horas)

### Objetivo
Scraper funcional para 1 plataforma con multiples direcciones y productos.

### Scope
| Elemento | Valor |
|----------|-------|
| Plataformas | 1 (Uber Eats) |
| Direcciones | 5-10 (diferentes zonas CDMX) |
| Productos | 3-5 (Big Mac, Combo, Nuggets, Coca-Cola) |
| Metricas | Precio, Delivery Fee, Service Fee, Tiempo estimado |
| Output | JSON file |

### Tareas
1. Parametrizar direcciones (lista de coordenadas)
2. Loop por cada direccion
3. Buscar restaurante de referencia (McDonald's)
4. Extraer todas las metricas disponibles
5. Guardar en JSON estructurado
6. Agregar logging basico
7. Agregar rate limiting (delays entre requests)

### Estructura de output
```json
{
  "scrape_id": "run_20260406_1430",
  "platform": "uber_eats",
  "timestamp": "2026-04-06T14:30:00",
  "results": [
    {
      "address": "Av. Reforma 222, CDMX",
      "lat": 19.4326,
      "lng": -99.1332,
      "zone_type": "centro",
      "restaurant": "McDonald's",
      "items": [
        {
          "name": "Big Mac",
          "price": 89.00,
          "currency": "MXN"
        }
      ],
      "delivery_fee": 29.00,
      "service_fee": 12.00,
      "estimated_time_min": 25,
      "estimated_time_max": 35,
      "promotions": ["20% off first order"],
      "available": true
    }
  ]
}
```

---

## MVP 2: Multi-Platform (6-8 horas)

### Objetivo
Extender a las 3 plataformas con la misma estructura de datos.

### Scope
| Elemento | Valor |
|----------|-------|
| Plataformas | 3 (Uber Eats + Rappi + DiDi Food) |
| Direcciones | 10-20 por plataforma |
| Productos | 3-5 estandarizados |
| Metricas | Todas las disponibles (min 3) |
| Output | JSON + CSV consolidado |

### Tareas
1. Crear scraper para Rappi (rappi.com.mx)
2. Crear scraper para DiDi Food (didi-food.com)
3. Normalizar schema de datos entre plataformas
4. Merge de resultados en CSV comparativo
5. Agregar retry logic basico
6. Agregar manejo de errores

### Arquitectura modular

```
src/
|-- scrapers/
|   |-- base_scraper.py      # Clase base con logica comun
|   |-- uber_eats.py          # Scraper Uber Eats
|   |-- rappi.py              # Scraper Rappi
|   |-- didi_food.py          # Scraper DiDi Food
|
|-- config/
|   |-- addresses.json        # Lista de direcciones
|   |-- products.json         # Productos de referencia
|   |-- settings.py           # Configuracion general
|
|-- output/
|   |-- raw/                  # JSON por plataforma
|   |-- merged/               # CSV consolidado
|
|-- main.py                   # Entry point: 1 comando
|-- requirements.txt
```

### CSV output esperado

```csv
timestamp,platform,address,zone_type,restaurant,product,price,delivery_fee,service_fee,total_price,est_time_min,est_time_max,promotions,available
2026-04-06T14:30,uber_eats,Reforma 222,centro,McDonalds,Big Mac,89.00,29.00,12.00,130.00,25,35,"20% off",true
2026-04-06T14:35,rappi,Reforma 222,centro,McDonalds,Big Mac,92.00,35.00,15.00,142.00,30,40,"",true
2026-04-06T14:40,didi_food,Reforma 222,centro,McDonalds,Big Mac,85.00,19.00,10.00,114.00,20,30,"Free delivery",true
```

---

## MVP 3: Insights & Visualizaciones (4-6 horas)

### Objetivo
Generar el informe de insights con visualizaciones a partir de los datos recolectados.

### Scope
| Elemento | Valor |
|----------|-------|
| Input | CSV consolidado del MVP 2 |
| Analisis | 5 dimensiones comparativas |
| Insights | Top 5 accionables |
| Graficos | Minimo 3 (barras, heatmap, comparativo) |
| Output | Notebook + PDF/HTML |

### Visualizaciones planificadas

1. **Grafico de barras:** Precio promedio por plataforma (Big Mac, Combo, etc.)
2. **Heatmap:** Competitividad por zona geografica (Rappi vs competidores)
3. **Grafico de barras apiladas:** Descomposicion del precio final (producto + delivery fee + service fee)
4. **Tabla comparativa:** Tiempos de entrega por plataforma y zona
5. **Grafico de radar:** Score competitivo multi-dimension por plataforma

### Template de Insight

```markdown
### Insight #N: [Titulo descriptivo]

**Finding:** [Que descubriste con datos especificos]

**Impacto:** [Por que es importante para Rappi - cuantificar si es posible]

**Recomendacion:** [Accion concreta que Rappi deberia tomar]

**Evidencia:** [Referencia al grafico/tabla que lo soporta]
```

### Herramientas
- **pandas** para analisis
- **matplotlib + seaborn** para graficos estaticos
- **plotly** para graficos interactivos (bonus)
- **Jupyter Notebook** como formato de trabajo
- Export a HTML/PDF para presentacion

---

## MVP 4: Polish & Presentacion (2-4 horas)

### Objetivo
Pulir todo para la presentacion de 30 minutos.

### Tareas
1. README.md completo con instrucciones de setup
2. Limpiar codigo y agregar comentarios donde sea necesario
3. Preparar datos pre-scrapeados como backup
4. Crear deck/slides con estructura sugerida del brief
5. Preparar demo (script que corre en vivo o grabacion)
6. Documentar limitaciones y next steps

---

## MVP 5 (Bonus): Dashboard Interactivo

### Solo si hay tiempo extra

- **Streamlit** app con:
  - Selector de zona/plataforma/producto
  - Graficos interactivos
  - Tabla de datos raw
  - Score competitivo por zona

---

## Timeline Sugerido (2 dias)

```
DIA 1 (8-10 horas)
===================
[Manana]
  09:00-11:00  MVP 0: Proof of concept (1 plataforma, 1 direccion)
  11:00-13:00  MVP 1: Multi-address scraping para UberEats

[Tarde]
  14:00-18:00  MVP 2: Agregar Rappi + DiDi Food
  18:00-19:00  Debugging + ajustes + recolectar datos finales

  --> Al final del Dia 1: Datos recolectados de 3 plataformas

DIA 2 (8-10 horas)
===================
[Manana]
  09:00-11:00  MVP 2 (cont): Completar scraping si faltan datos
  11:00-14:00  MVP 3: Analisis + insights + visualizaciones

[Tarde]
  14:00-16:00  MVP 3 (cont): Terminar informe
  16:00-18:00  MVP 4: README + cleanup + preparar presentacion
  18:00-19:00  Buffer: emergencias, demo test, backup data

  --> Al final del Dia 2: Sistema completo + informe + presentacion lista
```

---

## Criterios de Salida por MVP

| MVP | "Done" cuando... |
|-----|-------------------|
| MVP 0 | Puedo extraer 1 dato de 1 plataforma |
| MVP 1 | Tengo JSON con datos de 5+ direcciones de 1 plataforma |
| MVP 2 | Tengo CSV consolidado de 3 plataformas, 10+ direcciones |
| MVP 3 | Tengo 5 insights con graficos listos |
| MVP 4 | README funciona, demo lista, presentacion preparada |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Anti-bot bloquea scraping | Alta | Alto | Proxies + stealth + API interception |
| DOM cambia entre sesiones | Media | Medio | Selectores CSS robustos + fallbacks |
| Plataforma no disponible en zona | Baja | Medio | Probar multiples direcciones |
| Datos inconsistentes entre plataformas | Media | Medio | Schema de normalizacion bien definido |
| Se acaba el tiempo en MVP 2 | Media | Alto | Datos manuales como Plan B |
| Demo en vivo falla | Alta | Alto | Datos pre-scrapeados + grabacion de backup |
