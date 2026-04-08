# Guion Personal de Presentacion

> Este documento es **tu cheat sheet** para el dia de la presentacion.
> Tiene los scripts literales, las respuestas exactas a Q&A y los planes
> de contingencia narrativos. NO es documentacion del proyecto, es tu
> guion de actor.

**Para uso personal de:** [Tu nombre]
**Fecha de presentacion:** ____ / ____ / ____
**Duracion:** 20 min presentacion + 10 min Q&A

---

## Antes de empezar (15 min antes)

### Setup tecnico — checklist literal

```bash
# 1. Verificar internet
ping -c 3 google.com

# 2. Activar venv
cd c:/ProyectoEntrevistas/Rappi/SistemaCompetitiveIntelligence/desarrollo
source venv/Scripts/activate

# 3. Verificar Claude API
python -c "from src.utils.claude_client import ClaudeClient; print('OK' if ClaudeClient().is_available() else 'FAIL')"

# 4. Pre-generar el reporte (NO depender de internet en vivo)
python -m src.main --use-backup

# 5. Abrir en browser
start reports/insights.html   # Windows
```

### Pestanas del browser que debes tener listas

- [ ] Pestana 1: `reports/insights.html` (el reporte HTML)
- [ ] Pestana 2: https://github.com/wilcor7190/SistemaCompetitiveIntelligence (el repo)
- [ ] Pestana 3: https://www.rappi.com.mx/restaurantes/1306705702-mcdonalds (la pagina real)
- [ ] Pestana 4: VS Code con `data/merged/comparison_combined.csv`

### Terminales abiertas

- [ ] Terminal 1: `cd desarrollo && source venv/Scripts/activate` (lista para correr `--debug`)
- [ ] Terminal 2: Backup con `python -m src.main --use-backup` ya corrido

### Mental checklist

- [ ] Has dormido bien
- [ ] Tienes agua a la mano
- [ ] Tu camara esta funcionando
- [ ] Tu microfono esta funcionando
- [ ] Has hecho una prueba con el comando `--debug` HOY
- [ ] Sabes el primer parrafo del script de memoria

---

## Script Minuto a Minuto

### [0:00 - 2:00] Apertura (2 min)

#### Que decir literalmente:

> "Hola, soy [tu nombre] y voy a presentar el sistema que construi para el caso tecnico de Competitive Intelligence.
>
> El brief pedia un sistema que recolectara datos de 3 plataformas de delivery en Mexico, los normalizara y generara insights accionables.
>
> En lugar de construir un scraper tradicional, construi un **sistema de inteligencia con 3 capas de recoleccion** que se adapta automaticamente cuando una capa falla. Voy a mostrarles el sistema en accion en unos minutos."

#### Que mostrar:
- Slide titulo / o el README de GitHub abierto

#### Notas mentales:
- Habla pausado, no corras
- Sonrie al saludar
- Mira a la camara, no a tus notas

---

### [2:00 - 5:00] El Approach (3 min)

#### Que decir literalmente:

> "Hay 3 cosas que hacen este sistema diferente:
>
> **Primero**, las 3 capas de recoleccion. La idea es que el scraping es fragil — un cambio en el HTML puede romperlo todo. Mi sistema intenta primero interceptar las APIs internas. Si eso falla, hace parsing del DOM con selectores CSS verificados. Y si TODO falla, toma un screenshot y usa Claude vision para 'leer' los precios de la imagen como si fuera una persona.
>
> **Segundo**, generacion de insights con IA. Los datos crudos son utiles, pero el evaluador no quiere un CSV. Quiere saber 'por que importa esto para Rappi'. Use Claude Opus 4.6 para generar un resumen ejecutivo accionable.
>
> **Tercero**, resiliencia. El sistema tiene circuit breaker para pausar plataformas que estan bloqueando, retries automaticos, deduplicacion, validacion de rangos, y un modo backup que funciona sin internet. Garantiza que SIEMPRE hay datos para presentar."

#### Que mostrar:
- Diagrama de las 3 capas (puede ser uno simple en una slide o el ASCII del README)

#### Notas mentales:
- Enfatiza la palabra "automaticamente" en la primera capa
- Cuando digas "como si fuera una persona", haz una pausa breve
- Termina con conviccion: "Garantiza que SIEMPRE hay datos"

---

### [5:00 - 10:00] Demo en Vivo (5 min)

#### Que decir literalmente:

> "Vamos a ver el sistema corriendo. Voy a ejecutar el modo debug, que scrapea McDonald's en Rappi para una direccion de prueba."

#### Comando a ejecutar:

```bash
python -m src.main --debug
```

#### Mientras corre, narrar:

> "Aqui ven que esta lanzando un browser real con Playwright... esta navegando a la URL de McDonald's en Rappi... ya cargo la pagina... y aqui esta la magia: encontro 83 productos en el DOM, de los cuales 10 matchearon con los productos que estamos buscando.
>
> Mientras espera el rate limiter — porque tenemos delays aleatorios para no parecer un bot — fijense que ahora intenta Rappi Turbo para la conveniencia store, y aqui extrae 31 productos mas, incluyendo Coca-Cola por $19.
>
> Y al final, el sistema genera el resumen ejecutivo con Claude Opus 4.6."

#### Si algo falla:

> "Esto es exactamente para lo que disene el sistema. Tengo datos pre-scrapeados, vamos a generar el reporte con esos."

```bash
python -m src.main --use-backup
```

#### Despues de que termine:

> "Ahora vamos a ver el reporte que se genero."

#### Accion:
- Abrir `reports/insights.html` en el browser

#### Notas mentales:
- Si tarda, no llenes el silencio con "ehh" — explica que esta haciendo
- Si falla, NO te disculpes. Solo di "esto es exactamente para lo que diseñe..."
- Mantente confiado incluso si algo va mal

---

### [10:00 - 18:00] Recorrido del Reporte (8 min)

#### Que decir antes de abrir:

> "Este es el reporte HTML autocontenido que el sistema genera. Esta diseñado para que un VP de Strategy de Rappi lo abra en el browser sin instalar nada."

---

#### Seccion 1: Resumen Ejecutivo (2 min)

**Que hacer:** Leer en voz alta el resumen ejecutivo de Claude (o partes clave si es muy largo).

**Que decir despues de leer:**

> "Este parrafo lo genero Claude Opus 4.6 con los datos reales del CSV. Notese que cuantifica los hallazgos — Rappi tiene una ventaja de precio de 119% sobre Uber Eats, 100% de las observaciones tienen envio gratis — y termina con una recomendacion accionable especifica: cerrar la brecha de cobertura de catalogo."

**Notas:**
- Pausa despues de leer cada cifra clave
- Enfatiza "esto lo genero Claude" — es tu mayor diferenciador

---

#### Seccion 2: Datos del Scraping (1 min)

**Que decir:**

> "Aqui ven la tabla de cobertura. Recolectamos datos de Rappi y Uber Eats en multiples direcciones. La columna de Capas muestra que metodo se uso — DOM significa que los selectores CSS funcionaron, no necesite caer a vision."

---

#### Seccion 3: Comparativa de Precios (1 min)

**Que decir:**

> "Este chart compara precios producto por producto entre Rappi y Uber Eats. Las barras naranjas son Rappi, verdes son Uber. Pueden ver claramente donde Rappi es mas barato y donde no."

**Notas:**
- Apunta con el cursor a 1-2 productos especificos
- Si tienes ejemplo claro: "Aqui el Big Mac, Rappi $155 vs Uber $204"

---

#### Seccion 4: Top 5 Insights (3 min)

**Que decir:**

> "Estos son los 5 insights que el sistema genera, uno por cada dimension del brief:
>
> 1. **Posicionamiento de precios** — comparativa por plataforma
> 2. **Ventaja operacional** — tiempos de entrega
> 3. **Estructura de fees** — quien cobra mas envio
> 4. **Estrategia promocional** — quien tiene mas promos activas
> 5. **Variabilidad geografica** — diferencias por zona de CDMX
>
> Cada insight tiene Finding, Impacto, y Recomendacion. Esto es lo que importa para un equipo de pricing."

**Notas:**
- No leas los 5 insights completos (te toma muchos minutos)
- Enfocate en 1-2 con mas detalle
- Menciona la estructura: Finding/Impacto/Recomendacion

---

#### Seccion 5: Charts Adicionales (1 min)

**Que decir:**

> "Heatmap por zona, scatter de fee vs tiempo, y la tabla pivot. Todos generados automaticamente con matplotlib y seaborn."

---

### [18:00 - 20:00] Decisiones Tecnicas Clave (2 min)

#### Que decir literalmente:

> "Antes de pasar a preguntas, quiero mencionar 3 decisiones tecnicas:
>
> **Uno: priorice calidad sobre cobertura.** El brief dice claramente 'priorizar calidad'. Cuando DiDi Food no produjo datos en 2 horas — porque es una SPA vanilla con login requerido — lo documente como limitacion en lugar de pasar mas tiempo. Tengo 2 plataformas con datos verificados en lugar de 3 a medias.
>
> **Dos: empece con Ollama local pero migre a Claude API.** En la fase de diseño elegi modelos locales de Ollama por costo cero. Pero al implementar descubri que eran lentos, necesitaban 16 GB de modelos descargados, y la calidad de los insights era pobre. Migre a Claude API en MVP 4. La decision esta documentada en el ADR-005. El costo es ~$0.05 USD por ejecucion, despreciable.
>
> **Tres: el sistema tiene 130 tests automatizados.** Cada commit los corro. Esto me dio confianza para refactorizar agresivamente entre MVPs."

#### Notas mentales:
- Estos son tus 3 mejores puntos. Hazlos contar.
- Cuando digas "lo documente como limitacion" — muestra honestidad
- "130 tests" — di el numero con confianza

---

### [20:00 - 30:00] Q&A (10 min)

Tienes 9 preguntas pre-respondidas. Memoriza al menos las primeras 5.

---

#### P1: "¿Que pasa si te bloquean durante la demo?"

**Tu respuesta:**

> "Tengo 3 capas. Si la API interception falla, intento DOM parsing con selectores. Si los selectores cambian, tengo la Capa 3 con Claude vision que lee la imagen del screenshot. Y si todo falla, tengo el modo `--use-backup` con datos pre-scrapeados que ya verificaste hoy. En ningun escenario me quedo sin datos."

---

#### P2: "¿Por que migraste de Ollama a Claude?"

**Tu respuesta:**

> "Tres razones: velocidad, calidad y experiencia del evaluador.
>
> Ollama tardaba minutos en cargar modelos, generaba insights genericos y requeria que tu instalaras 16 GB de modelos.
>
> Claude API tarda 5 segundos, genera insights de calidad VP, y solo requiere una API key.
>
> La decision esta en el ADR-005 con todos los trade-offs."

---

#### P3: "¿Como escalarias esto a produccion?"

**Tu respuesta:**

> "Cuatro cosas:
>
> Uno, scheduler diario con cron para tracking temporal.
>
> Dos, mas ciudades — Monterrey, Guadalajara.
>
> Tres, API REST interna para que otros equipos consuman los insights.
>
> Cuatro, alertas: 'Uber bajo precios 10% en zona premium hoy'.
>
> La arquitectura de 3 capas escala bien porque cada plataforma es independiente."

---

#### P4: "¿Como manejas el rate limiting de las plataformas?"

**Tu respuesta:**

> "Tres mecanismos:
>
> Uno, rate limiter con delays aleatorios entre 3 y 7 segundos.
>
> Dos, circuit breaker que pausa una plataforma si mas del 60% de las ultimas 10 requests fallan.
>
> Tres, stealth flags en Playwright para no parecer bot."

---

#### P5: "Vi que DiDi Food no funciona. ¿Eso es un problema?"

**Tu respuesta:**

> "Es una limitacion documentada. DiDi Food es una SPA vanilla sin server-side rendering y aparentemente requiere login para ver el feed. Lo intente con localStorage hack, busqueda directa, y screenshots para Capa 3 — no produjo datos en 2 horas.
>
> El brief dice explicitamente 'priorizar calidad sobre cantidad'. Decidi que 2 plataformas bien scrapeadas son mas valiosas que 3 a medias. Lo documente honestamente en `pruebas/casos/mvp2-multi-platform.md` y en el reporte HTML.
>
> En produccion, con tiempo extra, intentaria con Selenium en lugar de Playwright o usaria un servicio como ScrapingBee para esa plataforma especifica."

---

#### P6: "¿Por que Playwright y no Selenium o Puppeteer?"

**Tu respuesta:**

> "Evalue varias opciones, esta en `Analisis/06-decision-matrix.md`. Playwright gano por cinco razones:
>
> Uno, API async nativa en Python — Selenium no la tiene.
>
> Dos, mejor manejo de SPAs modernas.
>
> Tres, network interception built-in, lo que hace la Capa 1 facil de implementar.
>
> Cuatro, stealth plugin maduro.
>
> Cinco, comunidad activa, mantenido por Microsoft."

---

#### P7: "¿Como pruebas el sistema?"

**Tu respuesta:**

> "130 tests con pytest, 100% passing. Cubro:
>
> - Tests unitarios de cada parser, normalizer, validator, merger
> - Tests de los modelos Pydantic
> - Tests de integracion con datos mock
> - Tests del scraper factory
> - Tests del HTML report
>
> NO testeo el scraping real porque seria flaky — depende de internet y la estructura del DOM. Eso lo verifico manualmente con `--debug` y documento en `pruebas/casos/`."

---

#### P8: "¿Cuanto te costo en credito de Claude?"

**Tu respuesta:**

> "Anthropic regala 5 dolares al crear cuenta. Use aproximadamente 50 centavos durante todo el desarrollo. Ejecutar el sistema una vez completo cuesta entre 1 y 5 centavos. Para una entrega como esta, el costo es despreciable."

---

#### P9: "¿Que aprendiste con este proyecto?"

**Tu respuesta:**

> "Tres cosas:
>
> Uno, las decisiones de diseño deben validarse en la implementacion. Ollama parecia genial en papel pero fue malo en la practica. Esta documentado en el ADR-005 como leccion aprendida.
>
> Dos, las abstracciones bien hechas habilitan cambios faciles. Migrar de Ollama a Claude tomo 2 horas porque toda la logica de IA estaba en un solo archivo.
>
> Tres, documentar limitaciones honestamente es mejor que ocultarlas. El evaluador valora mas un 'esto no funciono y aqui esta por que' que un 'todo funciona' que despues no funciona en la demo."

---

## Plan B Narrativo: Si Algo Falla en Vivo

### Falla 1: El scraping en vivo se cuelga

**Que decir:**

> "Esto es para lo que diseñe el modo backup. Tengo datos verificados de hoy."

**Que hacer:**
```bash
# Ctrl+C, luego:
python -m src.main --use-backup
```

---

### Falla 2: El browser no abre

**Que decir:**

> "Tengo el reporte HTML ya generado, vamos directo a el."

**Que hacer:**
- Cambiar a la pestana del browser donde ya esta abierto el HTML
- Si no esta abierto: `start reports/insights.html` (Windows)

---

### Falla 3: La API key de Claude se cae

**Que decir:**

> "El sistema funciona sin Claude. Hay un fallback determinístico con pandas que genera el resumen ejecutivo. Vamos a verlo."

**Que hacer:**
- Mostrar el reporte ya generado (no necesitas regenerarlo en vivo)

---

### Falla 4: No hay internet

**Que decir:**

> "El modo `--use-backup` no requiere internet ni para scraping ni para Claude (usa el reporte ya generado). Vamos a abrir directamente el reporte HTML."

**Que hacer:**
- Cambiar a la pestana del HTML pre-generado

---

### Falla 5: Una pregunta tecnica que no sabes responder

**Que decir:**

> "Buena pregunta. La decision esta documentada en `diseno/decisiones/ADR-XXX`, dejame revisar despues y te contesto en el follow-up."

**Notas:**
- No improvises ni inventes
- Mejor "no se" que mentir
- Sigue con la siguiente pregunta

---

## Frases Clave Para Recordar

Memoriza estas frases. Usalas durante la presentacion.

- "Sistema de inteligencia, no scraper"
- "3 capas con fallback automatico"
- "Garantiza datos en cualquier escenario"
- "Insights accionables, no solo numeros"
- "Calidad sobre cantidad" (cita textual del brief)
- "130 tests automatizados"
- "Documentado honestamente"
- "Costo despreciable, ~$0.05 USD por ejecucion"

---

## Lo Que NO Debes Decir

Estas frases te restan puntos. Evitalas:

- ❌ "No tuve tiempo de..." (suena a excusa)
- ❌ "Probe 5 cosas y nada funciono" (mejor: "Documente la limitacion en X")
- ❌ "El scraper a veces falla" (mejor: "El sistema tiene fallback automatico")
- ❌ "No estoy seguro" (mejor: "Voy a verificarlo en la documentacion")
- ❌ "Es solo un MVP" (es lo que pidieron, no te excuses)
- ❌ "Eh", "este", "o sea" (muletillas, respira en lugar de llenarlas)
- ❌ "Lo voy a explicar de manera simple" (suena condescendiente)

---

## Despues de la Presentacion

Inmediatamente:

1. Toma notas de las preguntas que te hicieron
2. Apunta lo que dijiste y lo que NO supiste responder
3. Si te piden el repo: ya esta publico → https://github.com/wilcor7190/SistemaCompetitiveIntelligence
4. Si te dicen "te contactamos" — agradece y termina con sonrisa

En las proximas 24 horas:

1. Envia un follow-up por email/LinkedIn agradeciendo la oportunidad
2. Si quedaron preguntas pendientes, respondelas en ese email
3. Incluye el link al repo y a tu CV/LinkedIn

---

## Tu mantra mental antes de empezar

> "Construi un sistema que funciona, esta documentado, esta testeado, y tengo datos reales. Si algo falla en vivo, tengo backup. No tengo nada que esconder. Voy a contar mi historia con confianza."

¡Suerte! 🚀
