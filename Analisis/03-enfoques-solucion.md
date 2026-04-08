# 03 - Enfoques de Solucion: Diferentes Formas de Resolver el Problema

## Overview de Enfoques

Hay **5 enfoques fundamentales** para obtener datos competitivos de delivery apps, cada uno con trade-offs distintos.

---

## Enfoque A: Web Scraping con Browser Automation

### Como funciona
Automatizar un browser (Chrome headless) que navega las versiones web de cada plataforma, simula una direccion, y extrae precios/fees/tiempos.

```
[Script Python] --> [Playwright/Nodriver] --> [Browser Headless]
                                                    |
                                          [ubereats.com/mx]
                                          [rappi.com.mx]
                                          [didi-food.com]
                                                    |
                                          [Extrae HTML/DOM]
                                                    |
                                          [Parsea datos] --> [CSV/JSON]
```

### Stack tipico
- **Playwright** (Python) + playwright-stealth
- **Nodriver** (Python) - mas nuevo, mejor anti-detection
- **SeleniumBase UC Mode** - Undetected ChromeDriver

### Pros
- Control total sobre que datos extraer
- Costo casi cero (solo proxies opcionales)
- Funciona con cualquier plataforma que tenga version web
- Reproducible y auditable

### Contras
- Mantenimiento: si cambia el DOM, se rompe
- Anti-bot: pueden bloquear, requiere stealth
- Velocidad: lento (browser rendering por cada request)
- Setup time: 1-3 dias por plataforma

### Viabilidad por plataforma

| Plataforma | Version Web | Dificultad | Notas |
|------------|-------------|------------|-------|
| Uber Eats | ubereats.com | Media | SPA React, necesita JS rendering |
| Rappi | rappi.com.mx | Media-Alta | SPA, posible Cloudflare |
| DiDi Food | didi-food.com | Media | Menos proteccion anti-bot |

### Estimacion de tiempo: **3-5 dias** para las 3 plataformas

---

## Enfoque B: Intercepcion de APIs Internas (Reverse Engineering)

### Como funciona
Analizar las network requests que hacen las apps/webs, identificar los endpoints API internos, y llamarlos directamente.

```
[Browser DevTools] --> [Analizar Network Tab]
                            |
                   [Identificar API endpoints]
                            |
               [POST /api/v3/stores?lat=X&lng=Y]
                            |
               [Requests Python directos] --> [JSON response]
                            |
               [Parsear y almacenar] --> [CSV/JSON]
```

### Stack tipico
- Chrome DevTools para reverse engineering
- **requests** o **httpx** (Python) para llamadas directas
- **mitmproxy** para interceptar trafico de apps moviles

### Pros
- **Mucho mas rapido** que browser automation (sin rendering)
- Datos mas limpios (ya vienen en JSON)
- Menos detectable (parece trafico normal de API)
- Mas estable (APIs cambian menos que el DOM)

### Contras
- Requiere tiempo de reverse engineering inicial
- APIs pueden tener auth tokens/signatures
- Tokens pueden expirar y necesitar refresh
- Zona gris legal mas profunda

### Viabilidad por plataforma

| Plataforma | API Publica | Dificultad RE | Auth requerido |
|------------|-------------|---------------|----------------|
| Uber Eats | No oficial | Media | Session token |
| Rappi | No oficial | Media-Alta | Posible API key |
| DiDi Food | No oficial | Alta | Desconocido |

### Estimacion de tiempo: **2-4 dias** (RE) + **1-2 dias** (implementacion)

---

## Enfoque C: Hibrido (Browser + API Interception)

### Como funciona
Usar browser automation para el login/setup inicial y capturar tokens, luego hacer requests directos a las APIs.

```
[Playwright] --> [Navegar a ubereats.com]
                        |
              [Interceptar network requests]
              [Capturar auth tokens/cookies]
                        |
              [Usar tokens en requests directos]
                        |
              [API calls rapidos sin browser] --> [JSON]
```

### Este es el enfoque mas pragmatico porque:
1. Playwright intercept network requests nativamente
2. Capturas cookies y tokens automaticamente
3. Usas browser solo cuando necesitas, API cuando puedes
4. Balance entre velocidad y confiabilidad

### Estimacion de tiempo: **2-3 dias** para las 3 plataformas

---

## Enfoque D: Scrapers Pre-construidos + Custom

### Como funciona
Usar Apify u otros scrapers existentes para Uber Eats, y construir custom solo para Rappi y DiDi Food.

```
[Apify Actor: Uber Eats Scraper] --> [Uber Eats data]
                                            |
[Custom Playwright: Rappi] --> [Rappi data] |
                                            |
[Custom Playwright: DiDi] --> [DiDi data]   |
                                            |
                              [Merge & Normalize] --> [CSV/JSON]
```

### Pros
- Rapido para Uber Eats (ya resuelto)
- Menos codigo que mantener
- Probado en produccion (scrapers de Apify)

### Contras
- Dependencia de terceros para UberEats
- Costo recurrente de Apify
- Inconsistencia entre fuentes de datos
- Aun necesitas custom para Rappi y DiDi

### Estimacion de tiempo: **1.5-3 dias**

---

## Enfoque E: Manual + Semi-automatizado (MVP Minimo)

### Como funciona
Scraping manual asistido por herramientas simples. Browser extensions + formularios + capturas de pantalla automatizadas.

```
[Chrome Extension] --> [Captura datos visibles]
                              |
                    [Formulario Google Sheets]
                              |
                    [Script Python procesa] --> [CSV]
```

### Herramientas
- **Data Miner** (Chrome extension)
- **Instant Data Scraper** (Chrome extension)
- **Screenshot + OCR** (Tesseract)
- Google Sheets como "base de datos"

### Pros
- Setup en **horas**, no dias
- No hay anti-bot issues
- Datos 100% verificados visualmente
- Excelente como Plan B / datos de backup

### Contras
- No escala
- Tedioso para 50 direcciones x 3 plataformas
- No automatizado realmente
- No impresiona tecnicamente

### Estimacion de tiempo: **0.5-1 dia** para datos basicos

---

## Tabla Comparativa de Enfoques

| Criterio | A: Browser | B: API RE | C: Hibrido | D: Pre-built+Custom | E: Manual |
|----------|-----------|-----------|------------|---------------------|-----------|
| **Velocidad scraping** | Lento | Rapido | Rapido | Medio | N/A |
| **Tiempo setup** | 3-5 dias | 3-6 dias | 2-3 dias | 1.5-3 dias | 0.5 dias |
| **Robustez** | Media | Alta | Alta | Media | Alta |
| **Mantenimiento** | Alto | Medio | Medio | Bajo-Medio | Alto |
| **Anti-bot risk** | Alto | Bajo | Medio | Variable | Ninguno |
| **Costo** | $0-50 | $0 | $0-50 | $50-200 | $0 |
| **Impresion tecnica** | Buena | Excelente | Excelente | Buena | Baja |
| **Escalabilidad** | Media | Alta | Alta | Media | Ninguna |
| **Complejidad** | Media | Alta | Media-Alta | Media | Baja |

---

## Recomendacion: Enfoque C (Hibrido) como Principal + E como Backup

### Por que:

1. **Cabe en 2 dias** (constraint principal del caso)
2. **Impresiona tecnicamente** - demuestra conocimiento de APIs + automation
3. **Pragmatico** - no over-engineer, usa lo que funcione mas rapido por plataforma
4. **Resiliente** - si una API falla, tienes browser automation como fallback
5. **El enfoque E (manual) como Plan B** garantiza tener datos para la presentacion

### Estrategia por plataforma:

```
Uber Eats  --> Intentar API interception primero, fallback a Playwright
Rappi      --> Playwright + interceptar APIs internas si es posible
DiDi Food  --> Playwright directo (menos informacion disponible sobre sus APIs)
```

### Diagrama de decision en runtime:

```
Para cada plataforma:
    |
    +-- Existe API descubierta?
    |       SI --> Usar requests directos
    |       NO --> Usar Playwright browser automation
    |
    +-- Scraping exitoso?
    |       SI --> Guardar datos en JSON
    |       NO --> Anti-bot detected?
    |               SI --> Rotar proxy + retry
    |               NO --> Log error + continuar con siguiente direccion
    |
    +-- Todos los datos recolectados?
            SI --> Merge + normalizar + exportar CSV/JSON
            NO --> Completar con datos manuales (Plan B)
```
