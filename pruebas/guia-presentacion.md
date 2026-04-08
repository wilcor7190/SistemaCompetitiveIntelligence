# Guia de Presentacion del Proyecto

> Documentacion oficial sobre la estructura, materiales y procedimientos
> para la presentacion del Sistema de Competitive Intelligence.

**Tipo de documento:** Especificacion de presentacion
**Audiencia:** Cualquier persona que vaya a presentar el proyecto
**Duracion total:** 30 minutos (20 min presentacion + 10 min Q&A)

---

## 1. Objetivos de la presentacion

La presentacion debe lograr 4 cosas:

1. **Demostrar el sistema funcionando** con datos reales o pre-scrapeados
2. **Explicar las decisiones tecnicas** clave del proyecto (ADRs)
3. **Mostrar los insights generados** y su valor de negocio
4. **Responder preguntas tecnicas** sobre arquitectura, escalabilidad y limitaciones

---

## 2. Audiencia objetivo

| Tipo | Que esperan ver |
|------|-----------------|
| **Evaluador tecnico** | Arquitectura, calidad de codigo, decisiones, tests |
| **Stakeholder de negocio** | Insights accionables, datos reales, ROI |
| **Hiring manager (AI Engineer)** | Como se uso IA, criterio tecnico, comunicacion |

---

## 3. Estructura de los 30 minutos

| Tiempo | Seccion | Contenido |
|--------|---------|-----------|
| **0:00 - 2:00** | Apertura | Introduccion personal y resumen del proyecto |
| **2:00 - 5:00** | Approach tecnico | 3 capas de recoleccion + IA + resiliencia |
| **5:00 - 10:00** | Demo en vivo | Ejecucion del sistema + output en consola |
| **10:00 - 18:00** | Recorrido del reporte HTML | 5 secciones del reporte de insights |
| **18:00 - 20:00** | Decisiones tecnicas | ADRs clave, especialmente ADR-005 |
| **20:00 - 30:00** | Q&A | Preguntas del evaluador |

---

## 4. Secciones de contenido

### 4.1 Apertura (2 min)

**Topicos a cubrir:**
- Quien presenta
- Que problema resuelve el sistema
- Cual es el diferenciador clave (no es solo un scraper)

### 4.2 Approach tecnico (3 min)

**Topicos a cubrir:**
- Arquitectura de 3 capas (API → DOM → Vision)
- Por que la resiliencia es importante (ante anti-bots y cambios de HTML)
- Rol de la IA en el sistema (Claude Opus 4.6 para insights)
- Sistema de fallback en caso de errores

### 4.3 Demo en vivo (5 min)

**Procedimiento:**
1. Ejecutar `python -m src.main --debug`
2. Narrar el comportamiento del sistema en tiempo real
3. Mostrar el JSON de salida
4. Si falla: ejecutar `python -m src.main --use-backup`

**Datos esperados a mostrar:**
- ~83 productos de McDonald's en Rappi
- Precio del Big Mac
- Delivery fee y tiempo de entrega
- Layer usado (DOM esperado)

### 4.4 Recorrido del reporte HTML (8 min)

**Archivo a abrir:** `reports/insights.html`

**Secciones a recorrer:**

| Seccion | Tiempo | Que mostrar |
|---------|--------|-------------|
| Resumen ejecutivo | 2 min | Texto narrativo generado por Claude |
| Datos del scraping | 1 min | Tabla de cobertura por plataforma |
| Comparativa de precios | 1 min | Bar chart Rappi vs Uber Eats |
| Top 5 insights | 3 min | Findings, impactos, recomendaciones |
| Charts adicionales | 1 min | Heatmap, scatter, tabla pivot |

### 4.5 Decisiones tecnicas (2 min)

**ADRs a mencionar:**

| ADR | Topico |
|-----|--------|
| ADR-002 | 3 capas con fallback automatico |
| ADR-003 | Service fee no accesible (decision consciente) |
| ADR-005 | Migracion de Ollama local a Claude API |

**Mensajes clave a transmitir:**
- "Calidad sobre cantidad" (cita del brief)
- 130 tests automatizados
- Decisiones validadas durante implementacion

### 4.6 Q&A (10 min)

Ver seccion 7 para los topicos esperados.

---

## 5. Materiales necesarios

### 5.1 Archivos del proyecto

| Item | Ubicacion |
|------|-----------|
| Reporte HTML pre-generado | `reports/insights.html` |
| Datos backup | `data/backup/` |
| CSV combinado | `data/merged/comparison_combined.csv` |
| Charts PNG individuales | `reports/charts/` |
| ADR-005 | `diseno/decisiones/ADR-005-migracion-ollama-a-claude.md` |
| Repositorio publico | https://github.com/wilcor7190/SistemaCompetitiveIntelligence |

### 5.2 Setup tecnico requerido

| Requisito | Verificacion |
|-----------|--------------|
| Python 3.10+ instalado | `python --version` |
| venv activado | Output `(venv)` en terminal |
| Dependencias instaladas | `pip list | grep playwright` |
| Chromium descargado | `playwright install chromium` |
| API Key Claude (opcional) | `.env` con `ANTHROPIC_API_KEY` |
| Internet | `ping google.com` |

### 5.3 Pestañas del browser a tener listas

1. `reports/insights.html` (reporte local)
2. https://github.com/wilcor7190/SistemaCompetitiveIntelligence (repo)
3. https://www.rappi.com.mx/restaurantes/1306705702-mcdonalds (pagina real para mostrar el origen de los datos)
4. CSV abierto en VS Code o Excel

### 5.4 Terminales a tener listas

1. **Terminal principal:** En `desarrollo/` con venv activado, lista para `--debug`
2. **Terminal backup:** Misma ubicacion, lista para `--use-backup`

---

## 6. Procedimientos de contingencia (Plan B)

### Falla 1: El scraping en vivo no responde

**Procedimiento:**
1. `Ctrl+C` para cancelar
2. Ejecutar `python -m src.main --use-backup`
3. Continuar la presentacion con datos pre-scrapeados

### Falla 2: El browser no abre el HTML

**Procedimiento:**
1. Verificar que `reports/insights.html` existe
2. Abrir manualmente con `start reports/insights.html` (Windows) o equivalente
3. Si tampoco funciona, mostrar el archivo en VS Code preview

### Falla 3: Sin conexion a Claude API

**Procedimiento:**
- El sistema continua con insights stats-based (fallback automatico)
- No requiere intervencion
- Mostrar el reporte ya pre-generado

### Falla 4: Sin internet

**Procedimiento:**
- Usar `--use-backup` (no requiere internet para scraping)
- El reporte HTML ya generado funciona sin internet
- Si Claude API estaba pre-llamada, su output ya esta en el HTML

### Falla 5: Pregunta tecnica que no se puede responder

**Procedimiento:**
- Indicar la ubicacion donde esta documentado: `diseno/decisiones/`
- Comprometerse a contestar en el follow-up
- Continuar con la siguiente pregunta

---

## 7. Topicos esperados en Q&A

El evaluador probablemente preguntara sobre:

| Categoria | Topicos |
|-----------|---------|
| **Resiliencia** | Que pasa si bloquean el scraping, manejo de Arkose, circuit breaker |
| **Arquitectura** | Por que 3 capas, escalabilidad, eleccion de Playwright |
| **IA** | Por que Claude API en lugar de Ollama, costo, alternativas |
| **Datos** | Calidad, validacion, normalizacion entre plataformas |
| **Limitaciones** | DiDi Food, service fee, productos no scrapeados |
| **Testing** | Cobertura, estrategia de tests, CI/CD |
| **Produccion** | Como se escalaria, monitoreo, alertas |
| **Costo** | Cuanto cuesta correr el sistema, presupuesto Claude API |

> **Nota:** El presentador debe preparar respuestas detalladas a estos
> topicos basandose en los ADRs documentados en `diseno/decisiones/`.

---

## 8. Resultados esperados

Despues de la presentacion, el evaluador deberia haber visto:

- ✅ El sistema funcionando en vivo (o con backup)
- ✅ El reporte HTML completo con 5 insights y 4 charts
- ✅ La arquitectura de 3 capas explicada
- ✅ Las decisiones tecnicas clave (ADRs)
- ✅ La honestidad sobre limitaciones (DiDi Food)
- ✅ La calidad del codigo (130 tests, ruff clean)
- ✅ Datos reales verificados de Rappi y Uber Eats

---

## 9. Documentos relacionados

| Documento | Proposito |
|-----------|-----------|
| [`checklists/pre-demo.md`](checklists/pre-demo.md) | Checklist del dia de la presentacion |
| [`checklists/pre-entrega.md`](checklists/pre-entrega.md) | Checklist pre-entrega |
| [`reportes/auditoria-tecnica-mvp4.md`](reportes/auditoria-tecnica-mvp4.md) | Auditoria tecnica completa |
| [`informe-auditoria-final.md`](informe-auditoria-final.md) | Informe final con todas las respuestas |
| [`../diseno/presentacion/estructura.md`](../diseno/presentacion/estructura.md) | Estructura original de la presentacion |
| [`../diseno/decisiones/`](../diseno/decisiones/) | ADRs (decisiones tecnicas documentadas) |
