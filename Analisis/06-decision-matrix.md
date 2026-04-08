# 06 - Matriz de Decision Tecnologica

## Decision 1: Framework de Browser Automation

| Criterio (peso) | Playwright (Python) | Nodriver | SeleniumBase UC | Scrapy |
|-----------------|:-------------------:|:--------:|:---------------:|:------:|
| Anti-bot bypass (30%) | 7 | 9 | 9 | 3 |
| Facilidad de uso (20%) | 9 | 7 | 7 | 6 |
| Documentacion (15%) | 9 | 6 | 7 | 9 |
| Async support (15%) | 10 | 8 | 5 | 8 |
| Network interception (10%) | 10 | 6 | 5 | 3 |
| Comunidad/soporte (10%) | 9 | 5 | 7 | 9 |
| **SCORE PONDERADO** | **8.5** | **7.3** | **7.0** | **5.7** |

### Decision: **Playwright (Python)**

**Razon:** Mejor balance entre facilidad de uso, network interception (clave para enfoque hibrido), y soporte async. Anti-bot se complementa con playwright-stealth plugin. Si Playwright falla por anti-bot, se puede escalar a Nodriver para plataformas especificas.

---

## Decision 2: Lenguaje de Programacion

| Criterio | Python | Node.js (TypeScript) | Go |
|----------|:------:|:--------------------:|:--:|
| Ecosystem scraping | 10 | 8 | 4 |
| Data analysis (pandas) | 10 | 5 | 3 |
| Visualizaciones | 10 | 7 | 2 |
| Playwright support | 9 | 10 | 0 |
| Velocidad desarrollo | 9 | 7 | 5 |
| Familiaridad equipo evaluador | 9 | 7 | 4 |
| **SCORE** | **9.5** | **7.3** | **3.0** |

### Decision: **Python 3.10+**

**Razon:** Dominante en data science, scraping, y analisis. pandas + matplotlib + Playwright = stack completo en un solo lenguaje. El equipo evaluador probablemente espera Python para un rol de AI Engineer.

---

## Decision 3: Formato de Output del Informe

| Criterio | Jupyter + HTML | Streamlit Dashboard | PowerPoint | PDF estatico |
|----------|:--------------:|:-------------------:|:----------:|:------------:|
| Tiempo de desarrollo | 8 | 5 | 3 | 7 |
| Interactividad | 6 | 10 | 2 | 1 |
| Impresion tecnica | 8 | 9 | 4 | 5 |
| Portabilidad | 9 | 5 | 8 | 10 |
| Reproducibilidad | 10 | 7 | 2 | 3 |
| **SCORE** | **8.2** | **7.2** | **3.8** | **5.2** |

### Decision: **Jupyter Notebook exportado a HTML** (principal) + **Streamlit** (bonus si hay tiempo)

**Razon:** Notebook es reproducible, muestra codigo + analisis + graficos en un solo lugar. HTML es portable para compartir. Streamlit es bonus de alto impacto visual.

---

## Decision 4: Manejo de Proxies

| Opcion | Costo | Setup | Efectividad |
|--------|-------|-------|-------------|
| Sin proxies | $0 | Ninguno | Baja - riesgo alto de bloqueo |
| ScraperAPI | $49/mes | API key | Alta - residential proxies |
| Bright Data | $500+/mes | Complejo | Muy alta - pero caro |
| Proxies gratuitos | $0 | Medio | Muy baja - no confiable |
| VPN rotativo | $10/mes | Bajo | Media |

### Decision: **Empezar sin proxies, escalar a ScraperAPI si hay bloqueos**

**Razon:** No gastar dinero hasta validar que es necesario. Rate limiting + stealth pueden ser suficientes para 20-50 requests.

---

## Decision 5: Almacenamiento de Datos

| Opcion | Pros | Contras | Veredicto |
|--------|------|---------|-----------|
| **JSON files** | Simple, legible, schema flexible | No queryable facilmente | Para datos raw |
| **CSV** | Universal, Excel-compatible | Tipos de datos limitados | Para datos merged |
| **SQLite** | Queryable, relacional | Over-engineering para este scope | No |
| **PostgreSQL** | Produccion-ready | Requiere setup, innecesario | No |

### Decision: **JSON (raw) + CSV (consolidado)**

**Razon:** El brief pide CSV o JSON. Usar ambos: JSON para preservar estructura completa, CSV para analisis y compartir.

---

## Decision 6: Estrategia de Direcciones

| Enfoque | Direcciones | Pros | Contras |
|---------|-------------|------|---------|
| **Pocas y diversas** | 20-25 | Calidad > cantidad, analisis profundo | Menor representatividad |
| **Muchas basicas** | 50 | Mayor cobertura | Datos superficiales, mas riesgo de bloqueo |
| **Por clusters** | 30 (6 clusters x 5) | Balance, permite analisis por zona | Mas complejo de justificar |

### Decision: **25-30 direcciones en 5-6 clusters**

```
Cluster 1: Centro/Turismo    (5 dirs) - Alta competencia
Cluster 2: Premium/Polanco   (5 dirs) - Tickets altos
Cluster 3: Residencial Sur   (5 dirs) - Volumen constante
Cluster 4: Periferia Este    (5 dirs) - Zona de expansion
Cluster 5: Corporativo/Santa Fe (5 dirs) - Hora pico almuerzo
Cluster 6: Norte/Expansion   (3-5 dirs) - Baja cobertura (opcional)
```

**Razon:** Permite analisis de variabilidad geografica (requisito del informe) sin saturar las plataformas con demasiados requests.

---

## Decision 7: Productos de Referencia

| Categoria | Producto | Por que |
|-----------|----------|---------|
| Fast Food | **Big Mac** | Indice Big Mac es estandar mundial, disponible en todas las plataformas |
| Fast Food | **Combo Mediano McDonalds** | Compara bundling y pricing de combos |
| Fast Food | **Nuggets 10 pz** | Producto simple, buen punto de comparacion |
| Retail | **Coca-Cola 600ml** | Producto commoditizado, precio deberia ser similar |
| Retail | **Agua Bonafont 1L** | Bajo precio, amplifica diferencias en fees |

### Decision: **5 productos (3 fast food + 2 retail)**

**Razon:** 5 productos x 3 plataformas x 25 direcciones = 375 data points. Suficiente para analisis estadistico sin ser excesivo.

---

## Stack Final Seleccionado

```
STACK TECNOLOGICO FINAL
========================

Scraping:
  - Playwright (Python) con playwright-stealth
  - Fallback: Nodriver para plataformas problematicas
  - Network interception para APIs internas

Anti-detection:
  - playwright-stealth (base)
  - Random delays 3-7s entre requests
  - User-Agent rotativo (Chrome Mexico)
  - ScraperAPI (solo si hay bloqueos)

Lenguaje: Python 3.10+

Analisis:
  - pandas (manipulacion datos)
  - matplotlib + seaborn (graficos estaticos)
  - plotly (graficos interactivos, bonus)

Informe:
  - Jupyter Notebook (desarrollo)
  - HTML export (entrega)
  - Streamlit (bonus dashboard)

Datos:
  - JSON (raw por plataforma)
  - CSV (consolidado para analisis)

Automatizacion:
  - Script bash (run.sh)
  - CLI con argparse

Versionamiento:
  - Git + GitHub (repositorio publico)
```

---

## Diagrama de Dependencias

```
requirements.txt
=================
playwright>=1.40
playwright-stealth>=1.0
pandas>=2.0
matplotlib>=3.7
seaborn>=0.12
plotly>=5.15
jupyter>=1.0
python-dotenv>=1.0
pydantic>=2.0        # Validacion de schemas
rich>=13.0           # Logging bonito en consola
aiohttp>=3.9         # Requests async (API interception)
```

---

## Riesgos por Decision

| Decision | Riesgo | Mitigacion |
|----------|--------|------------|
| Playwright como principal | Anti-bot mas sofisticado que stealth | Fallback a Nodriver o API interception |
| Python unico lenguaje | Ninguno significativo | N/A |
| Sin proxies inicialmente | Bloqueo en primeros intentos | Tener cuenta ScraperAPI lista |
| JSON+CSV sin DB | No queryable para analisis complejos | pandas suple esta necesidad |
| 25 direcciones | Podria ser insuficiente | Facil agregar mas en config |
| 5 productos | Podria no mostrar variabilidad | Cubren fast food + retail |
