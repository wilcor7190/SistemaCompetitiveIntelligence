# Guia Practica de Presentacion — Caso Tecnico Rappi

> Esta guia es para el dia de la presentacion. Tiene script literal,
> backup plans y respuestas a preguntas dificiles.

## Formato

- **Duracion total:** 30 minutos
- **Presentacion:** 20 minutos
- **Q&A:** 10 minutos
- **Demo en vivo:** 5 minutos (incluido en los 20)

## Antes de empezar (15 min antes)

### Setup tecnico

```bash
# 1. Verificar internet
ping -c 3 google.com

# 2. Activar venv
cd c:/ProyectoEntrevistas/Rappi/SistemaCompetitiveIntelligence/desarrollo
source venv/Scripts/activate

# 3. Verificar Claude API
python -c "from src.utils.claude_client import ClaudeClient; print('OK' if ClaudeClient().is_available() else 'FAIL')"

# 4. Pre-generar el reporte (asi no dependes de internet en vivo)
python -m src.main --use-backup

# 5. Abrir en browser
start reports/insights.html   # Windows
open reports/insights.html    # macOS
```

### Tener listas estas pestañas en el browser

1. `reports/insights.html` (el reporte HTML)
2. https://github.com/wilcor7190/SistemaCompetitiveIntelligence (el repo)
3. https://www.rappi.com.mx/restaurantes/1306705702-mcdonalds (para mostrar la pagina real)
4. Tu CSV en VS Code (`data/merged/comparison_combined.csv`)

### Tener listas estas terminales

1. **Terminal 1:** `cd desarrollo && source venv/Scripts/activate` (lista para correr `--debug`)
2. **Terminal 2:** Backup con `python -m src.main --use-backup` ya ejecutado

---

## Script Minuto a Minuto

### [0:00 - 2:00] Apertura (2 min)

**Que decir:**

> "Hola, soy [tu nombre] y voy a presentar el sistema que construi para el caso tecnico de Competitive Intelligence.
>
> El brief pedia un sistema que recolectara datos de 3 plataformas de delivery en Mexico, los normalizara y generara insights accionables.
>
> En lugar de construir un scraper tradicional, construi un **sistema de inteligencia con 3 capas de recoleccion** que se adapta automaticamente cuando una capa falla. Voy a mostrarles el sistema en accion en unos minutos."

**Que mostrar:**
- Slide titulo / o el README de GitHub abierto

---

### [2:00 - 5:00] El Approach (3 min)

**Que decir:**

> "Hay 3 cosas que hacen este sistema diferente:
>
> **Primero**, las 3 capas de recoleccion. La idea es que el scraping es fragil — un cambio en el HTML puede romperlo todo. Mi sistema intenta primero interceptar las APIs internas. Si eso falla, hace parsing del DOM con selectores CSS verificados. Y si TODO falla, toma un screenshot y usa Claude vision para 'leer' los precios de la imagen como si fuera una persona.
>
> **Segundo**, generacion de insights con IA. Los datos crudos son utiles, pero el evaluador no quiere un CSV. Quiere saber 'por que importa esto para Rappi'. Use Claude Opus 4.6 para generar un resumen ejecutivo accionable.
>
> **Tercero**, resiliencia. El sistema tiene circuit breaker para pausar plataformas que estan bloqueando, retries automaticos, deduplicacion, validacion de rangos, y un modo backup que funciona sin internet. Garantiza que SIEMPRE hay datos para presentar."

**Que mostrar:**
- Diagrama de las 3 capas (puede ser uno simple en una slide)

---

### [5:00 - 10:00] Demo en Vivo (5 min)

**Que decir:**

> "Vamos a ver el sistema corriendo. Voy a ejecutar el modo debug, que scrapea McDonald's en Rappi para una direccion de prueba."

**Comando a ejecutar:**

```bash
python -m src.main --debug
```

**Mientras corre, narrar:**

> "Aqui ven que esta lanzando un browser real con Playwright... esta navegando a la URL de McDonald's en Rappi... ya cargo la pagina... y aqui esta la magia: encontro 83 productos en el DOM, de los cuales 10 matchearon con los productos que estamos buscando.
>
> Mientras espera el rate limiter — porque tenemos delays aleatorios para no parecer un bot — fijense que ahora intenta Rappi Turbo para la conveniencia store, y aqui extrae 31 productos mas, incluyendo Coca-Cola por $19.
>
> Y al final, el sistema genera el resumen ejecutivo con Claude Opus 4.6."

**Si algo falla:**

> "Esto es exactamente para lo que disene el sistema. Tengo datos pre-scrapeados, vamos a generar el reporte con esos."

```bash
python -m src.main --use-backup
```

**Despues de que termine:**

> "Ahora vamos a ver el reporte que se genero."

**Abrir** `reports/insights.html` **en el browser.**

---

### [10:00 - 18:00] Recorrido del Reporte (8 min)

> "Este es el reporte HTML autocontenido que el sistema genera. Esta diseñado para que un VP de Strategy de Rappi lo abra en el browser sin instalar nada."

#### Seccion 1: Resumen Ejecutivo (2 min)

**Leer en voz alta el resumen ejecutivo de Claude.**

> "Este parrafo lo genero Claude Opus 4.6 con los datos reales del CSV. Notese que cuantifica los hallazgos — Rappi tiene una ventaja de precio de 119% sobre Uber Eats, 100% de las observaciones tienen envio gratis — y termina con una recomendacion accionable especifica: cerrar la brecha de cobertura de catalogo."

#### Seccion 2: Datos del Scraping (1 min)

> "Aqui ven la tabla de cobertura. Recolectamos datos de Rappi y Uber Eats en multiples direcciones. La columna de Capas muestra que metodo se uso — DOM significa que los selectores CSS funcionaron, no necesite caer a vision."

#### Seccion 3: Comparativa de Precios (1 min)

> "Este chart compara precios producto por producto entre Rappi y Uber Eats. Las barras naranjas son Rappi, verdes son Uber. Pueden ver claramente donde Rappi es mas barato y donde no."

#### Seccion 4: Top 5 Insights (3 min)

> "Estos son los 5 insights que el sistema genera, uno por cada dimension del brief:
> 1. **Posicionamiento de precios** — comparativa por plataforma
> 2. **Ventaja operacional** — tiempos de entrega
> 3. **Estructura de fees** — quien cobra mas envio
> 4. **Estrategia promocional** — quien tiene mas promos activas
> 5. **Variabilidad geografica** — diferencias por zona de CDMX
>
> Cada insight tiene Finding, Impacto, y Recomendacion. Esto es lo que importa para un equipo de pricing."

#### Seccion 5: Charts Adicionales (1 min)

> "Heatmap por zona, scatter de fee vs tiempo, y la tabla pivot. Todos generados automaticamente con matplotlib y seaborn."

---

### [18:00 - 20:00] Decisiones Tecnicas Clave (2 min)

> "Antes de pasar a preguntas, quiero mencionar 3 decisiones tecnicas:
>
> **Uno: priorice calidad sobre cobertura.** El brief dice claramente 'priorizar calidad'. Cuando DiDi Food no produjo datos en 2 horas — porque es una SPA vanilla con login requerido — lo documente como limitacion en lugar de pasar mas tiempo. Tengo 2 plataformas con datos verificados en lugar de 3 a medias.
>
> **Dos: empece con Ollama local pero migre a Claude API.** En la fase de diseño elegi modelos locales de Ollama por costo cero. Pero al implementar descubri que eran lentos, necesitaban 16 GB de modelos descargados, y la calidad de los insights era pobre. Migre a Claude API en MVP 4. La decision esta documentada en el ADR-005. El costo es ~$0.05 USD por ejecucion, despreciable.
>
> **Tres: el sistema tiene 130 tests automatizados.** Cada commit los corro. Esto me dio confianza para refactorizar agresivamente entre MVPs."

---

### [20:00 - 30:00] Q&A (10 min)

**Preparate para estas preguntas:**

#### P1: "¿Que pasa si te bloquean durante la demo?"

> "Tengo 3 capas. Si la API interception falla, intento DOM parsing con selectores. Si los selectores cambian, tengo la Capa 3 con Claude vision que lee la imagen del screenshot. Y si todo falla, tengo el modo `--use-backup` con datos pre-scrapeados que ya verificaste hoy. En ningun escenario me quedo sin datos."

#### P2: "¿Por que migraste de Ollama a Claude?"

> "Tres razones: velocidad, calidad y experiencia del evaluador. Ollama tardaba minutos en cargar modelos, generaba insights genericos y requeria que tu instalaras 16 GB de modelos. Claude API tarda 5 segundos, genera insights de calidad VP, y solo requiere una API key. La decision esta en el ADR-005 con todos los trade-offs."

#### P3: "¿Como escalarias esto a produccion?"

> "Cuatro cosas:
> 1. Scheduler diario con cron para tracking temporal
> 2. Mas ciudades — Monterrey, Guadalajara
> 3. API REST interna para que otros equipos consuman los insights
> 4. Alertas: 'Uber bajo precios 10% en zona premium hoy'
>
> La arquitectura de 3 capas escala bien porque cada plataforma es independiente."

#### P4: "¿Como manejas el rate limiting de las plataformas?"

> "Tres mecanismos:
> 1. Rate limiter con delays aleatorios entre 3-7 segundos
> 2. Circuit breaker que pausa una plataforma si >60% de las ultimas 10 requests fallan
> 3. Stealth flags en Playwright para no parecer bot (no `--no-sandbox` en produccion seria mejor, lo se)"

#### P5: "Vi que DiDi Food no funciona. ¿Eso es un problema?"

> "Es una limitacion documentada. DiDi Food es una SPA vanilla sin server-side rendering y aparentemente requiere login para ver el feed. Lo intente con localStorage hack, busqueda directa, y screenshots para Capa 3 — no produjo datos en 2 horas.
>
> El brief dice explicitamente 'priorizar calidad sobre cantidad'. Decidi que 2 plataformas bien scrapeadas son mas valiosas que 3 a medias. Lo documente honestamente en `pruebas/casos/mvp2-multi-platform.md` y en el reporte HTML.
>
> En produccion, con tiempo extra, intentaria con Selenium en lugar de Playwright o usaria un servicio como ScrapingBee para esa plataforma especifica."

#### P6: "¿Por que Playwright y no Selenium o Puppeteer?"

> "Evalue varias opciones (esta en `Analisis/06-decision-matrix.md`). Playwright gano por:
> 1. API async nativa en Python (Selenium no la tiene)
> 2. Mejor manejo de SPAs modernas
> 3. Network interception built-in (Capa 1 facil de implementar)
> 4. Stealth plugin maduro
> 5. Comunidad activa, mantenido por Microsoft"

#### P7: "¿Como pruebas el sistema?"

> "130 tests con pytest, 100% passing. Cubro:
> - Tests unitarios de cada parser, normalizer, validator, merger
> - Tests de los modelos Pydantic
> - Tests de integracion con datos mock
> - Tests del scraper factory
> - Tests del HTML report
>
> NO testeo el scraping real porque seria flaky — depende de internet y la estructura del DOM. Eso lo verifico manualmente con `--debug` y documento en `pruebas/casos/`."

#### P8: "¿Cuanto te costo en credito de Claude?"

> "Anthropic regala $5 USD al crear cuenta. Use ~$0.50 USD durante todo el desarrollo. Ejecutar el sistema una vez completo cuesta entre $0.01 y $0.05 USD. Para una entrega como esta, el costo es despreciable."

#### P9: "¿Que aprendiste con este proyecto?"

> "Tres cosas:
> 1. **Las decisiones de diseño deben validarse en la implementacion.** Ollama parecia genial en papel pero fue malo en la practica. Esta documentado en el ADR-005 como leccion aprendida.
> 2. **Las abstracciones bien hechas habilitan cambios faciles.** Migrar de Ollama a Claude tomo 2 horas porque toda la logica de IA estaba en un solo archivo.
> 3. **Documentar limitaciones honestamente es mejor que ocultarlas.** El evaluador valora mas un 'esto no funciono y aqui esta por que' que un 'todo funciona' que despues no funciona en la demo."

---

## Plan B: Si Algo Falla en Vivo

### Falla 1: El scraping en vivo se cuelga

```bash
# Ctrl+C, luego:
python -m src.main --use-backup
```

> "Esto es para lo que diseñe el modo backup. Tengo datos verificados de hoy."

### Falla 2: El browser no abre

> "Tengo el reporte HTML ya generado, vamos directo a el."

(Abrir `reports/insights.html` en el browser ya cargado)

### Falla 3: La API key de Claude se cae

> "El sistema funciona sin Claude. Hay un fallback determinístico con pandas que genera el resumen ejecutivo. Vamos a verlo."

(Mostrar el reporte ya generado, no necesitas regenerarlo en vivo)

### Falla 4: No hay internet

> "El modo `--use-backup` no requiere internet ni para scraping ni para Claude (usa el reporte ya generado). Vamos a abrir directamente el reporte HTML."

### Falla 5: Una pregunta tecnica que no sabes responder

> "Buena pregunta. La decision esta documentada en `diseno/decisiones/ADR-XXX`, dejame revisar despues y te contesto en el follow-up."

---

## Materiales Listos

| Item | Ubicacion | Verificado? |
|------|-----------|-------------|
| Reporte HTML pre-generado | `reports/insights.html` | [ ] |
| Datos backup | `data/backup/` | [ ] |
| CSV combinado | `data/merged/comparison_combined.csv` | [ ] |
| Charts PNG | `reports/charts/` | [ ] |
| Repo en GitHub | https://github.com/wilcor7190/SistemaCompetitiveIntelligence | [ ] |
| ADR-005 (migracion Claude) | `diseno/decisiones/ADR-005-migracion-ollama-a-claude.md` | [ ] |
| README con prerequisitos | `README.md` | [ ] |

## Frases Clave Para Recordar

- "Sistema de inteligencia, no scraper"
- "3 capas con fallback automatico"
- "Garantiza datos en cualquier escenario"
- "Insights accionables, no solo numeros"
- "Calidad sobre cantidad" (cita textual del brief)
- "130 tests automatizados"
- "Documentado honestamente"
- "Costo $0.05 USD por ejecucion"

## Lo Que NO Debes Decir

- ❌ "No tuve tiempo de..." (suena a excusa)
- ❌ "Probe 5 cosas y nada funciono" (mejor: "Documente la limitacion en X")
- ❌ "El scraper a veces falla" (mejor: "El sistema tiene fallback automatico")
- ❌ "No estoy seguro" (mejor: "Voy a verificarlo en la documentacion")
- ❌ "Es solo un MVP" (es lo que pidieron, no te excuses)

## Despues de la Presentacion

1. Tomar notas de las preguntas que te hicieron
2. Apuntar lo que dijiste y lo que no supiste responder
3. Si te piden el repo, ya esta publico: https://github.com/wilcor7190/SistemaCompetitiveIntelligence
4. Enviar follow-up con las respuestas a preguntas pendientes (si aplica)
