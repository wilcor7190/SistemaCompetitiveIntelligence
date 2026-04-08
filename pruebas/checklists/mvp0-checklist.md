# Checklist: MVP 0 — PoC Rappi

**Fecha:** ____-__-__
**Branch:** feature/poc-rappi
**Tag:** v0.1.0-alpha

---

## Automatizados

- [ ] `pytest tests/ -v` pasa 100% (35 tests)
- [ ] `ruff check src/` sin errores

## Manuales

- [ ] `python -m src.main --debug` ejecuta sin crash
- [ ] Se obtiene al menos 1 dato real de Rappi (o se documenta razon de fallo)
- [ ] JSON de salida es valido y tiene campos requeridos (platform, address, items, fees)
- [ ] Logger muestra output legible en consola con timestamps y niveles

## Datos

- [ ] ScrapedResult tiene campos: platform, address, store_name, scrape_layer, success
- [ ] Si success=True: al menos 1 item con name y price > 0
- [ ] Si success=False: error_message explica la razon

## Seguridad

- [ ] No hay secrets en el codigo (.env, API keys, passwords)
- [ ] `.env` no esta commiteado (verificar `.gitignore`)
- [ ] `data/raw/`, `data/merged/`, `data/screenshots/` estan en `.gitignore`

## Codigo

- [ ] schemas.py implementa todos los modelos del diseno
- [ ] config.py carga settings.yaml, addresses.json, products.json
- [ ] base.py tiene logica de 3 capas (API → DOM → Vision stub)
- [ ] rappi.py implementa extract_items, extract_fees, extract_delivery_time
- [ ] main.py tiene --debug funcional
- [ ] logger.py usa rich para output en consola
- [ ] ollama_client.py no crashea si Ollama no esta disponible
