# 02 - Analisis de Mercado: Herramientas y Alternativas

## Panorama del Mercado de Competitive Intelligence

El mercado de price monitoring esta valuado en ~$1.2B (2024) con proyeccion a $2.5B para 2033 (CAGR 9.2%). El web scraping services market crece de $512M a $762M (2026-2034).

---

## Categoria 1: Plataformas SaaS de Price Intelligence

Soluciones llave en mano que combinan scraping + matching + analytics.

| Plataforma | Precio | Fortaleza | Limitacion para este caso |
|-----------|--------|-----------|--------------------------|
| **Prisync** | Desde $99/mes | Tracking historico, stock, bulk | Enfocado en e-commerce, no delivery apps |
| **Price2Spy** | Desde $57.95/mes | Alertas real-time, presupuesto bajo | No soporta apps moviles/delivery |
| **Competera** | Enterprise | AI para pricing optimo, ML | Overkill y caro para este scope |
| **Skuuudle** | Enterprise | Matching automatico de productos | Orientado a retail, no delivery |
| **Dealavo** | Custom | Multi-marketplace | Sin soporte para LATAM delivery |
| **Wiser** | Enterprise | Omnichannel tracking | Pricing enterprise, no aplica |

**Veredicto:** Estas plataformas estan disenadas para e-commerce/retail tradicional. **No sirven directamente** para monitorear delivery apps como Uber Eats o DiDi Food porque:
- No scrape an apps moviles ni sus versiones web
- No manejan el concepto de "delivery fee" + "service fee" + "precio producto"
- No tienen cobertura en LATAM delivery market

---

## Categoria 2: Scrapers Pre-construidos (Apify, Octoparse)

Herramientas con scrapers listos para usar en delivery platforms.

| Herramienta | Modelo | Plataformas Soportadas | Precio |
|-------------|--------|----------------------|--------|
| **Apify - Uber Eats Scraper** | Pay per result | Uber Eats | ~$5/1K resultados |
| **Apify - DoorDash Scraper** | Pay per result | DoorDash | ~$5/1K resultados |
| **Apify - Food Delivery Monitor** | Pay per result | UberEats + DoorDash + Grubhub | Variable |
| **Octoparse** | Suscripcion | Cualquier sitio web (no-code) | Desde $89/mes |
| **DoubleData** | Enterprise | Multi-plataforma delivery | Custom |

**Datos que extraen:**
- Menus completos con precios
- Delivery fees y service fees
- Ratings y reviews
- Tiempos de entrega estimados
- Disponibilidad de restaurantes

**Limitacion clave:** 
- **No hay scrapers pre-hechos para Rappi ni DiDi Food en Apify**
- Los existentes son para mercado USA (DoorDash, Grubhub)
- Uber Eats scraper si podria funcionar para Mexico

---

## Categoria 3: Scraping APIs / Proxy Services

Servicios que simplifican el scraping tecnico.

| Servicio | Que ofrece | Precio | Utilidad |
|----------|-----------|--------|----------|
| **ScraperAPI** | API proxy + rendering JS | Desde $49/mes | Evitar bloqueos, rotar IPs |
| **Bright Data** | Proxies residenciales + scraper IDE | Desde $500/mes | Proxies LATAM, anti-detection |
| **Oxylabs** | Web Scraper API | Desde $49/mes (17.5K results) | API estructurada |
| **ScrapingBee** | API scraping + headless Chrome | Desde $49/mes | Simple, JS rendering |
| **Scrapfly** | Anti-bot bypass + API | Desde $30/mes | Bypass Cloudflare |
| **Crawlee** | Framework open-source | Gratis | Libreria Node.js por Apify |

---

## Categoria 4: Frameworks Open Source (Build your own)

| Framework | Lenguaje | Anti-bot | Curva aprendizaje |
|-----------|----------|----------|-------------------|
| **Playwright** | Python/Node/C# | playwright-stealth plugin | Media |
| **Selenium + SeleniumBase UC** | Python | Undetected ChromeDriver | Media-Alta |
| **Nodriver** | Python | Nativo anti-detection | Media |
| **Puppeteer** | Node.js | puppeteer-stealth (deprecated) | Media |
| **Scrapy** | Python | Con middlewares | Alta |
| **BeautifulSoup + requests** | Python | Ninguno (solo HTML estatico) | Baja |

### Estado del Arte Anti-Bot (2026):

```
EFECTIVIDAD DE BYPASS (de mayor a menor):

1. Nodriver / SeleniumBase UC Mode  --> Mejor opcion actual
2. Playwright + stealth + proxies   --> Buena opcion, mas versatil  
3. Puppeteer-stealth                --> DEPRECATED (Feb 2025)
4. FlareSolverr                     --> Ya no funciona con Cloudflare actual

DETECCION PRINCIPAL:
- navigator.webdriver flag
- Chrome DevTools Protocol (CDP) signatures
- Fingerprinting del browser
- Cloudflare Turnstile / AI Labyrinth (2025+)
```

---

## Categoria 5: Servicios de Scraping Especializados en Food Delivery

| Empresa | Servicio | Mercados |
|---------|----------|----------|
| **Actowiz Solutions** | DoorDash/UberEats data scraping | USA |
| **FoodDataScrape** | iFood menu & pricing scraper | Brasil/LATAM |
| **ScrapingPros** | Multi-platform food delivery | Global |
| **Diya Infotech** | Food delivery app scraping | USA/India |
| **RealDataAPI** | Uber Eats Food API scraping | Global |

**Modelo:** Generalmente son servicios de consultoria/agencia, no self-service. Precio por proyecto o por volumen de datos.

---

## Como Resuelven Esto Otras Empresas

### iFood (Brasil)
- Domina con 80%+ market share en Brasil
- Delivery fee ~$0.6 USD (vs Rappi ~$1.5 USD)
- Usa contratos exclusivos con restaurantes como barrera competitiva

### Rappi (segun Sacra Research)
- Valuacion ~$7B, "el Meituan de LATAM"
- Super-app model: food + groceries + pharmacy + fintech
- Compete en Mexico, Colombia, Chile, Argentina, Peru, Brasil

### Practicas comunes de la industria:
1. **Scraping automatizado** de menus y precios de competidores
2. **Price dashboards** internos para tracking de tendencias
3. **Dynamic pricing models** alimentados por data competitiva
4. **Mystery shopping digital** - ordenar en competidores para medir experiencia

---

## Mapa de Alternativas por Costo vs Control

```
ALTO CONTROL
    ^
    |  [Custom Playwright/Nodriver]
    |     Costo: $0-50/mes (proxies)
    |     Tiempo: 2-5 dias setup
    |     Mantenimiento: Alto
    |
    |  [Crawlee + ScraperAPI]
    |     Costo: $49-100/mes
    |     Tiempo: 1-3 dias setup
    |     Mantenimiento: Medio
    |
    |  [Apify Actors + Custom]
    |     Costo: $49-200/mes
    |     Tiempo: 0.5-2 dias
    |     Mantenimiento: Bajo-Medio
    |
    |  [SaaS (Prisync, etc)]
    |     Costo: $100-500+/mes
    |     Tiempo: 0.5 dias setup
    |     Mantenimiento: Bajo
    |     PERO: No soporta delivery apps
    v
BAJO CONTROL -----> ALTO COSTO
```

---

## Conclusion del Analisis de Mercado

**No existe una solucion off-the-shelf que resuelva este caso especifico** porque:

1. Las plataformas SaaS de pricing estan enfocadas en e-commerce, no en delivery apps
2. Los scrapers pre-hechos existen para UberEats/DoorDash (USA) pero **no para Rappi ni DiDi Food Mexico**
3. Se necesita desarrollo custom para al menos 2 de las 3 plataformas

**Recomendacion:** Enfoque hibrido:
- **Uber Eats:** Reusar/adaptar scrapers existentes (Apify o custom)
- **Rappi + DiDi Food:** Desarrollo custom con Playwright o Nodriver
- **Infraestructura:** ScraperAPI o proxies basicos para anti-detection
