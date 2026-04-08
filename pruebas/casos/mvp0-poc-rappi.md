# Casos de Prueba — MVP 0: PoC Rappi

**MVP:** 0
**Branch:** feature/poc-rappi
**Tag:** v0.1.0-alpha

---

## Caso: TC-001 — Modelos Pydantic crean instancias validas

**Componente:** Models (schemas.py)
**Prioridad:** Alta
**Tipo:** Unitario (automatizado)

### Precondiciones
- `desarrollo/src/models/schemas.py` implementado
- `pytest` instalado en venv

### Pasos
1. Ejecutar `cd desarrollo && pytest tests/test_models.py -v`

### Resultado Esperado
- Address se crea con datos validos (label, lat, lng, zone_type)
- Address rechaza latitud fuera de [-90, 90]
- Address rechaza longitud fuera de [-180, 180]
- ScrapedItem se crea con precio valido (>0, <=10000)
- ScrapedItem rechaza precio <= 0
- FeeInfo se crea con defaults (todos None/vacios)
- FeeInfo rechaza fees negativos
- Platform tiene 3 valores: rappi, uber_eats, didi_food
- StoreType tiene 3 valores: restaurant, convenience, pharmacy
- ZoneType tiene 6 valores
- ScrapeLayer tiene 5 valores
- TimeEstimate rechaza minutos > 180
- ScrapedResult se crea con items, fees, time_estimate
- ScrapingRun calcula success_rate y layer_distribution

### Resultado Real
_Llenar al ejecutar_

### Estado
No ejecutado

---

## Caso: TC-002 — Config carga los 3 archivos de configuracion

**Componente:** Config (config.py)
**Prioridad:** Alta
**Tipo:** Unitario (automatizado)

### Precondiciones
- `desarrollo/config/settings.yaml` existe
- `desarrollo/config/addresses.json` existe con 25 direcciones
- `desarrollo/config/products.json` existe con 3 store_groups

### Pasos
1. Ejecutar `cd desarrollo && pytest tests/test_config.py -v`

### Resultado Esperado
- `Config.load()` carga los 3 archivos sin error
- `get_addresses()` retorna 25 direcciones
- Direcciones cubren 5 zone_types: centro, premium, residencial, periferia, corporativo
- `get_store_groups()` retorna 3 grupos: restaurant, convenience, pharmacy
- Restaurant group tiene 3 productos (Big Mac, McNuggets, Combo Mediano)
- Todos los productos tienen aliases y expected_price_range
- `get_platforms()` retorna [rappi, uber_eats, didi_food] en orden (ADR-001)
- `get_scraper_config()` retorna ScraperConfig con valores validos
- `get_ollama_config()` retorna OllamaConfig con modelos esperados
- `get_paths()` tiene keys: raw_data, merged_data, screenshots, reports

### Resultado Real
_Llenar al ejecutar_

### Estado
No ejecutado

---

## Caso: TC-003 — RappiScraper navega a McDonald's y extrae 1 precio

**Componente:** Scraper (rappi.py)
**Prioridad:** Alta
**Tipo:** E2E (manual)

### Precondiciones
- Playwright Chromium instalado (`playwright install chromium`)
- Conexion a internet
- `desarrollo/src/scrapers/rappi.py` implementado

### Pasos
1. Ejecutar `cd desarrollo && python -m src.main --debug`
2. Observar que el browser se abre (headless=false)
3. Verificar que navega a `rappi.com.mx/restaurantes/1306705702-mcdonalds`
4. Observar el output en consola
5. Verificar el JSON de salida

### Resultado Esperado
- Browser abre sin crash
- Navega a la URL de McDonald's en Rappi
- Si Layer 1 (API) o Layer 2 (DOM) extraen datos:
  - Al menos 1 item con nombre y precio > 0
  - Fee info (puede ser null si no se encuentra)
  - Time estimate (puede ser null)
- Si ambas capas fallan:
  - ScrapedResult con success=False
  - Error message descriptivo
  - Screenshot guardado en data/screenshots/
- Logger muestra progreso legible

### Resultado Real
_Llenar al ejecutar_

### Estado
No ejecutado

---

## Caso: TC-004 — CLI --debug ejecuta sin errores

**Componente:** CLI (main.py)
**Prioridad:** Alta
**Tipo:** E2E (manual)

### Precondiciones
- venv activado con dependencias instaladas
- Playwright Chromium instalado

### Pasos
1. Ejecutar `cd desarrollo && python -m src.main --debug`
2. Observar output en consola
3. Verificar que el programa termina (exit code 0 o 3)

### Resultado Esperado
- `--debug` aplica overrides: platforms=rappi, max_addresses=1, headless=false
- Logger configurado en nivel DEBUG (mas verbose)
- Config se carga correctamente
- Ollama availability check no crashea (warning si no disponible)
- RappiScraper se inicializa y ejecuta
- Browser se cierra al terminar (teardown)
- Programa termina con exit code 0 (exito) o 3 (scraping fallo, pero no crash)
- No hay tracebacks no manejados

### Resultado Real
_Llenar al ejecutar_

### Estado
No ejecutado
