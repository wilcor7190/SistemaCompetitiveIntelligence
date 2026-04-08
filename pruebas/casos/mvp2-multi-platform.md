# Casos de Prueba — MVP 2: Multi-Platform

**MVP:** 2
**Branch:** feature/multi-platform
**Tag:** v0.2.0

---

## Caso: TC-201 — UberEatsScraper navega y extrae datos

**Componente:** UberEatsScraper
**Prioridad:** Alta
**Tipo:** E2E (manual)

### Pasos
1. Ejecutar `python -m src.main --platforms uber_eats --max-addresses 1 --headless`

### Resultado Esperado
- Navega a ubereats.com/mx brand page de McDonald's
- Si Arkose bloquea: log warning, intenta Layer 3 (vision)
- Si no bloquea: extrae productos con precios
- No crashea en ningun caso

### Estado
No ejecutado

---

## Caso: TC-202 — DiDiFoodScraper con localStorage hack

**Componente:** DiDiFoodScraper
**Prioridad:** Media
**Tipo:** E2E (manual)

### Pasos
1. Ejecutar `python -m src.main --platforms didi_food --max-addresses 1 --headless`

### Resultado Esperado
- Inyecta direccion en localStorage
- Busca McDonald's en DiDi Food
- Extrae datos si la pagina carga, o documenta fallo
- Decision de corte: si falla completamente, se documenta

### Estado
No ejecutado

---

## Caso: TC-203 — Arkose detection no bloquea el pipeline

**Componente:** UberEatsScraper._check_arkose
**Prioridad:** Alta
**Tipo:** Unitario (automatizado)

### Pasos
1. Ejecutar `pytest tests/test_scrapers.py -v`

### Resultado Esperado
- UberEatsScraper detecta iframe de Arkose
- Retorna False (no intenta resolver CAPTCHA)
- Escala a Layer 3 (vision) automaticamente

### Estado
No ejecutado

---

## Caso: TC-204 — CSV tiene datos de >=2 plataformas

**Componente:** DataMerger multi-platform
**Prioridad:** Alta
**Tipo:** Integracion (automatizado)

### Pasos
1. Ejecutar `pytest tests/test_integration.py -v`

### Resultado Esperado
- DataFrame con datos de rappi + uber_eats (+ didi_food si funciona)
- Cada plataforma tiene su propia fila por producto/direccion
- Columna `platform` distingue correctamente

### Estado
No ejecutado

---

## Caso: TC-205 — Mismo producto comparable entre plataformas

**Componente:** Integration pipeline
**Prioridad:** Alta
**Tipo:** Integracion (automatizado)

### Pasos
1. Ejecutar `pytest tests/test_integration.py::TestMultiPlatformMerge -v`

### Resultado Esperado
- Big Mac aparece con precio diferente por plataforma
- Misma direccion, mismo producto, diferente platform + precio
- No hay deduplicacion entre plataformas (solo dentro de misma plataforma)

### Estado
No ejecutado

---

## Caso: TC-206 — Scraper factory crea scraper correcto

**Componente:** ScrapingOrchestrator._create_scraper
**Prioridad:** Alta
**Tipo:** Unitario (automatizado)

### Pasos
1. Ejecutar `pytest tests/test_scrapers.py::TestScraperFactory -v`

### Resultado Esperado
- Platform.RAPPI -> RappiScraper
- Platform.UBER_EATS -> UberEatsScraper
- Platform.DIDI_FOOD -> DiDiFoodScraper

### Estado
No ejecutado
