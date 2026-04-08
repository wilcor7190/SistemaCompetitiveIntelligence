# Casos de Prueba — MVP 1: Rappi Completo

**MVP:** 1
**Branch:** feature/rappi-scraper
**Tag:** v0.1.0

---

## Caso: TC-101 — Orchestrator recorre direcciones sin crash

**Componente:** ScrapingOrchestrator
**Prioridad:** Alta
**Tipo:** E2E (manual)

### Precondiciones
- venv activado, Playwright instalado

### Pasos
1. Ejecutar `python -m src.main --platforms rappi --max-addresses 3 --headless`
2. Observar que recorre las 3 direcciones sin crash

### Resultado Esperado
- Orchestrator itera por cada direccion y store group
- No hay tracebacks no manejados
- Programa termina con exit code 0 o 3
- Raw JSON guardado en data/raw/

### Resultado Real
_Llenar al ejecutar_

### Estado
No ejecutado

---

## Caso: TC-102 — Multi-store funciona (McDonald's + Oxxo)

**Componente:** RappiScraper multi-store
**Prioridad:** Alta
**Tipo:** E2E (manual)

### Precondiciones
- Conexion a internet

### Pasos
1. Ejecutar `python -m src.main --platforms rappi --max-addresses 1 --headless`
2. Verificar logs para restaurant y convenience

### Resultado Esperado
- Restaurant (McDonald's): SUCCESS con items y precios
- Convenience (Oxxo/Turbo): SUCCESS o FAIL documentado
  - Si falla: error_message explica razon (selectores diferentes)
- El fallo de convenience NO detiene el pipeline

### Resultado Real
_Llenar al ejecutar_

### Estado
No ejecutado

---

## Caso: TC-103 — Normalizacion parsea precios correctamente

**Componente:** DataNormalizer
**Prioridad:** Alta
**Tipo:** Unitario (automatizado)

### Pasos
1. Ejecutar `pytest tests/test_normalizer.py -v`

### Resultado Esperado
- "$145.00" -> 145.0
- "Gratis" -> 0.0
- "" -> None
- "$139-149" -> 139.0 (toma minimo)
- "25-35 min" -> (25, 35)
- "35 min" -> (35, 35)
- Detecta keywords de promo: "gratis", "off", "descuento", "2x1"
- 22 tests pasando

### Estado
No ejecutado

---

## Caso: TC-104 — Product matching resuelve aliases conocidos

**Componente:** ProductMatcher
**Prioridad:** Alta
**Tipo:** Unitario (automatizado)

### Pasos
1. Ejecutar `pytest tests/test_product_matcher.py -v`

### Resultado Esperado
- "big mac" -> "Big Mac" (alias exacto)
- "big mac tocino" -> "Big Mac" (variante)
- "BIG MAC" -> "Big Mac" (case insensitive)
- "McFlurry Oreo" -> None (no esta en aliases)
- Cosine similarity funciona correctamente
- 13 tests pasando

### Estado
No ejecutado

---

## Caso: TC-105 — CSV se genera con columnas correctas

**Componente:** DataMerger
**Prioridad:** Alta
**Tipo:** Unitario (automatizado)

### Pasos
1. Ejecutar `pytest tests/test_merger.py -v`

### Resultado Esperado
- DataFrame tiene 24 columnas del schema
- Deduplicacion funciona (misma plataforma+direccion+producto)
- Resultados fallidos no se incluyen
- Promotions se unen con ";"
- 7 tests pasando

### Estado
No ejecutado

---

## Caso: TC-106 — Circuit breaker se activa si >=60% fallan

**Componente:** ScrapingOrchestrator
**Prioridad:** Media
**Tipo:** Manual (observar logs)

### Pasos
1. Ejecutar scraping con muchas direcciones
2. Si >60% fallan en 10 consecutivas, verificar log "CIRCUIT BREAKER"

### Resultado Esperado
- Log muestra "CIRCUIT BREAKER: X% failures" si umbral se alcanza
- Plataforma se pausa, no crashea
- Otras plataformas continuan

### Estado
No ejecutado (requiere muchos fallos consecutivos)

---

## Caso: TC-107 — Rate limiter respeta delays de settings.yaml

**Componente:** BaseScraper.rate_limit_delay
**Prioridad:** Media
**Tipo:** Manual (observar timing)

### Pasos
1. Ejecutar con --debug (logging DEBUG)
2. Observar logs de "Rate limit delay: X.Xs"

### Resultado Esperado
- Delays entre 3-7 segundos (settings.yaml: delay_between_requests_min/max)
- Delays son aleatorios (no siempre iguales)

### Estado
No ejecutado

---

## Caso: TC-108 — Screenshots se guardan con naming correcto

**Componente:** Screenshot utility
**Prioridad:** Baja
**Tipo:** Manual

### Pasos
1. Ejecutar scraping que falle en alguna direccion
2. Verificar data/screenshots/

### Resultado Esperado
- Formato: {platform}_{address-slug}_{YYYYMMDD}_{HHMMSS}.png
- Ejemplo: rappi_reforma-222_20260407_214856.png
- Screenshot es legible (no negro)

### Estado
No ejecutado
