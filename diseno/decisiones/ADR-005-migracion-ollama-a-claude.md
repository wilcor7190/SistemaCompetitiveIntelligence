# ADR-005: Migracion de Ollama Local a Claude API (Anthropic)

**Estado:** Aceptado
**Fecha:** 2026-04-08
**Supersede:** Decisiones de modelos en ADR-002 (parcialmente)
**Relacionado:** `Analisis/07-modelos-ollama-aplicacion.md`

## Contexto

En la fase de diseno (Analisis y diseno/), se eligio **Ollama local** como proveedor de IA para 3 funciones del sistema:

| Funcion | Modelo Ollama elegido | Tamano |
|---------|----------------------|--------|
| OCR de screenshots (Capa 3) | `qwen3-vl:8b` | ~6 GB |
| Parseo de texto roto (Capa 2 fallback) | `qwen3.5:4b` | ~3 GB |
| Generacion de insights | `qwen3.5:9b` | ~6 GB |
| Product matching (embeddings) | `nomic-embed-text` | ~300 MB |

**Total:** ~16 GB de modelos descargados + Ollama corriendo en background.

### Razones originales para elegir Ollama (validas en su momento)

- **Costo cero**: sin facturas de API
- **Privacidad**: datos nunca salen de la maquina
- **Sin vendor lock-in**: modelos open source
- **Tema del puesto**: AI Engineer, mostrar uso de LLMs locales

Estas razones se documentaron en `Analisis/07-modelos-ollama-aplicacion.md` y se reflejaron en `diseno/arquitectura/prompts-ollama.md`, `componentes.md`, y `tolerancia-fallos.md`.

## Problema

Durante la implementacion del MVP 4 (polish y validacion final), se encontraron problemas operacionales con Ollama que no fueron evidentes en la fase de diseno:

### 1. Lentitud inaceptable

- **Ollama tarda 30-90 segundos** en cargar un modelo en RAM la primera vez
- Cada llamada subsecuente: 5-15 segundos
- En modo `--debug`, el sistema **se colgaba** despues de "Starting run" porque Ollama estaba ocupado cargando modelos
- El usuario presiono Ctrl+C en una prueba en vivo despues de esperar > 1 minuto

### 2. Calidad de insights insuficiente

- `qwen3.5:9b` genera resumenes ejecutivos genericos y poco accionables
- Para un VP de Strategy de Rappi (audiencia objetivo), la calidad era inaceptable
- Comparacion en la misma data:

**Ollama (qwen3.5:9b)**:
> "Analisis de 2 plataformas de delivery en 2 direcciones de CDMX con 71 productos. Se identificaron oportunidades en pricing, fees y cobertura geografica."

**Claude Opus 4.6 (post-migracion)**:
> "Rappi mantiene un posicionamiento de precio promedio de $113.19 MXN frente a los $248.36 MXN de Uber Eats, lo que representa una ventaja competitiva de **119.4% en precio** que debe comunicarse de forma mas agresiva al consumidor. (...) La recomendacion mas urgente es **cerrar la brecha de cobertura de catalogo —actualmente al 67%— incorporando los 35 productos faltantes**, ya que sin disponibilidad completa la ventaja de precio pierde capacidad de conversion frente a usuarios que migran a Uber Eats simplemente por encontrar alli lo que buscan."

### 3. Friccion de instalacion para evaluadores

Un evaluador del caso tecnico tendria que:
1. Instalar Ollama (~50 MB de instalador)
2. Descargar 4 modelos (~16 GB de transferencia)
3. Esperar a que Ollama arranque y cargue modelos
4. Tener al menos 8 GB de RAM libre durante la ejecucion

Esto contradice el principio de "el evaluador clona y corre el sistema" del MVP 4.

### 4. Falta de RAM en maquinas tipicas

- `qwen3.5:9b` requiere ~6 GB de RAM dedicada
- Combinado con Chrome (Playwright) + Python + sistema operativo: ~12+ GB de RAM total
- Maquinas de desarrollo tipicas (8-16 GB) sufren swapping y lentitud extrema

## Decision

**Migrar de Ollama local a Claude API (Anthropic)** para todas las funciones de IA del sistema, manteniendo el sistema **funcional sin API key** mediante fallbacks deterministicos.

### Cambios concretos

| Funcion | Antes (Ollama) | Despues (Claude API) | Fallback sin API key |
|---------|---------------|---------------------|---------------------|
| Insights ejecutivos | `qwen3.5:9b` | `claude-opus-4-6` | Template stats-based con pandas |
| Vision OCR (Capa 3) | `qwen3-vl:8b` | Claude vision API | Layer 3 deshabilitada (Capas 1-2 funcionan) |
| Text parser (Capa 2 fallback) | `qwen3.5:4b` | Claude API | Regex fallback |
| Product matching | `nomic-embed-text` | Eliminado | Alias normalizado (siempre activo, suficiente) |

### Modelo elegido: Claude Opus 4.6

Siguiendo el principio del SDK de Anthropic: **default to Opus 4.6** salvo que el usuario explicite lo contrario. Razones:
- Calidad estado del arte para insights de negocio
- Soporta vision nativa (necesario para Capa 3)
- 200K context window (suficiente para todos los CSVs del proyecto)

## Alternativas Consideradas

### A. Mantener Ollama y optimizar - RECHAZADA
- **Pro:** Cero cambios en codigo, sigue siendo gratis
- **Contra:** No resuelve la lentitud (limite del hardware local)
- **Contra:** No mejora calidad de insights
- **Contra:** Friccion de instalacion sigue existiendo

### B. Migrar a Claude API solo para insights - RECHAZADA
- **Pro:** Migracion parcial, menos cambios
- **Contra:** Inconsistencia (2 proveedores de IA en el mismo sistema)
- **Contra:** Sigue requiriendo Ollama para Capa 3

### C. Usar OpenAI o Gemini en lugar de Claude - RECHAZADA
- **Pro:** Posiblemente mas barato (Gemini Flash)
- **Contra:** Menor calidad de razonamiento que Opus 4.6
- **Contra:** El diseno ya esta abstraido (cambiar de proveedor es facil en el futuro)
- **Contra:** Documentacion del SDK de Anthropic disponible via skill

### D. Migrar a Claude API con fallback stats-based (ACEPTADA)
- **Pro:** Velocidad: ~5-10s por consulta (vs minutos con Ollama)
- **Pro:** Calidad: Opus 4.6 genera resumenes de calidad VP
- **Pro:** Setup trivial: 1 API key (vs 16 GB de modelos)
- **Pro:** Sistema sigue funcionando sin API key (degraded mode)
- **Pro:** Costo bajo: ~$0.01-$0.05 USD por ejecucion
- **Contra:** Requiere API key (no es 100% local)
- **Contra:** Vendor lock-in con Anthropic (mitigado: la abstraccion `ClaudeClient` permite cambio futuro)

## Consecuencias

### Positivas

- **Velocidad 6-10x**: ejecuciones que tardaban minutos ahora tardan segundos
- **Calidad de insights drasticamente mejor**: resumenes accionables con narrativa profesional
- **Setup simplificado**: 1 API key vs 16 GB de modelos
- **Confiabilidad**: cero crashes/cuelgues vs problemas frecuentes con Ollama
- **Onboarding del evaluador**: 1 minuto (crear key) vs 30+ minutos (instalar y descargar)
- **Sistema sigue funcionando sin API key**: insights stats-based como fallback deterministico
- **Codigo mas limpio**: `ClaudeClient` (153 lineas) vs `OllamaClient` (119 lineas) con menos error handling necesario

### Negativas

- **Costo recurrente**: ~$0.01-$0.05 USD por ejecucion (mitigado: $5 USD gratis al registrarse, suficiente para ~100 ejecuciones)
- **Dependencia de internet**: la Capa 3 requiere conexion (mitigado: Capas 1-2 funcionan offline; modo `--use-backup` para demos sin internet)
- **Vendor lock-in con Anthropic**: si Claude se cae o sube precios, hay impacto (mitigado: la abstraccion `src/utils/claude_client.py` permite cambiar de proveedor con ~30 min de trabajo)
- **Menor "wow factor" de IA local**: ya no se puede decir "todo corre en mi maquina" (mitigado: el sistema funciona sin API key, asi que tecnicamente sigue siendo posible correr 100% local)

### Impacto en costos reales

| Escenario | Llamadas a Claude | Costo aproximado |
|-----------|-------------------|------------------|
| 1 ejecucion `--use-backup` (insights solamente) | 1 | $0.005 USD |
| 1 ejecucion `--debug` (1 dir + insights) | 1 | $0.01 USD |
| 1 ejecucion completa (3 dirs x 2 plataformas + insights) | 1-2 | $0.02 USD |
| 1 ejecucion full (25 dirs x 2 plataformas + insights + Capa 3 ocasional) | 2-5 | $0.05-$0.15 USD |

**Costo proyectado para evaluacion del caso:** < $1 USD total.

## Implementacion

### Archivos creados
- `desarrollo/src/utils/claude_client.py` - Wrapper async (chat + vision)

### Archivos eliminados
- `desarrollo/src/utils/ollama_client.py`

### Archivos modificados (8)
- `desarrollo/src/main.py` - removido Ollama check, agregado Claude check
- `desarrollo/src/scrapers/orchestrator.py` - usa ClaudeClient
- `desarrollo/src/scrapers/base.py` - Layer 3 con Claude vision
- `desarrollo/src/scrapers/vision_fallback.py` - reescrito para Claude vision API
- `desarrollo/src/scrapers/text_parser.py` - reescrito para Claude API
- `desarrollo/src/processors/product_matcher.py` - simplificado a solo aliases
- `desarrollo/src/analysis/insights.py` - executive summary con Claude Opus 4.6
- `desarrollo/.env.example` - `ANTHROPIC_API_KEY` reemplaza `OLLAMA_BASE_URL`

### Tests
- 130/130 tests pasando despues de la migracion
- Test de `executive_summary` actualizado para probar el template fallback (no requiere API key en CI)

### Configuracion del usuario
```bash
# Antes (Ollama)
ollama pull qwen3-vl:8b
ollama pull qwen3.5:4b
ollama pull qwen3.5:9b
ollama pull nomic-embed-text
# Total: ~16 GB de descarga

# Despues (Claude API)
cp .env.example .env
# Editar .env y pegar ANTHROPIC_API_KEY
# Total: 1 API key
```

## Estado de los Documentos de Diseno

Este ADR **no invalida** los documentos de las fases `Analisis/` y `diseno/` que mencionan Ollama:

- `Analisis/07-modelos-ollama-aplicacion.md` - **valido como contexto historico** (justifica por que se eligio Ollama originalmente)
- `diseno/arquitectura/prompts-ollama.md` - **valido como referencia de prompts** (los prompts son los mismos, solo cambia el cliente que los ejecuta)
- `diseno/arquitectura/componentes.md` - menciona OllamaClient, **valido como diseno original**
- `diseno/arquitectura/tolerancia-fallos.md` - menciona "Ollama no disponible", **conceptualmente sigue aplicando** (Claude API no disponible = mismo fallback)
- `diseno/decisiones/ADR-002` - menciona qwen models, **valido como decision tomada en su momento**

**Lectura recomendada para evaluadores:**
1. Leer la fase `Analisis/` y `diseno/` para entender la planeacion original
2. Leer este ADR-005 para entender la evolucion en la fase de implementacion
3. El codigo en `desarrollo/src/` refleja el estado final

Este patron (decisiones de diseno + ADRs de cambios) es practica estandar en software profesional. Reescribir los documentos de diseno borraria la historia del proyecto y ocultaria una decision tecnica relevante.

## Lecciones Aprendidas

1. **Las decisiones de diseno deben validarse en la implementacion**: lo que parece bueno en papel puede fallar en la practica. Los problemas de Ollama solo se hicieron evidentes al usarlo en condiciones reales.

2. **La velocidad importa para la experiencia del evaluador**: un sistema que tarda minutos en arrancar pierde puntos vs uno que tarda segundos, independientemente de la calidad final.

3. **Costo no es el unico factor**: el "costo cero" de Ollama tenia un costo oculto en tiempo, friccion de setup, y calidad de output.

4. **Fallbacks deterministicos son oro**: la decision de mantener insights stats-based como fallback significa que el sistema funciona aun sin API key. Esto preserva la propiedad "el evaluador puede correrlo en cualquier escenario".

5. **Las abstracciones bien hechas habilitan cambios faciles**: la migracion completa tomo ~2 horas porque toda la logica de IA estaba aislada en un solo archivo (`ollama_client.py`). Reemplazar por `claude_client.py` con la misma interfaz fue trivial.
