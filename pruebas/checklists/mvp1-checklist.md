# Checklist: MVP 1 — Rappi Completo

**Fecha:** ____-__-__
**Branch:** feature/rappi-scraper
**Tag:** v0.1.0

---

## Automatizados

- [ ] `pytest tests/ -v` pasa 100% (94 tests: models + config + normalizer + matcher + merger + validator)
- [ ] `ruff check src/` sin errores

## Manuales

- [ ] `python -m src.main --platforms rappi --max-addresses 3 --headless` ejecuta OK
- [ ] comparison.csv se genera en data/merged/
- [ ] Raw JSON se guarda en data/raw/
- [ ] `--save-backup` genera archivos en data/backup/
- [ ] `--dry-run` muestra plan sin ejecutar

## Datos

- [ ] CSV tiene datos de al menos restaurant (McDonald's)
- [ ] Success rate >= 50% (restaurant funciona, convenience puede fallar)
- [ ] Precios en rango razonable ($40-$500 MXN)
- [ ] delivery_fee, delivery_time, rating presentes para restaurant
- [ ] Deduplicacion funciona (no hay filas duplicadas)

## Funcionalidades MVP 1

- [ ] Orchestrator recorre addresses x store_groups
- [ ] Circuit breaker implementado (>=60% fallos = pausa)
- [ ] Rate limiter con delays aleatorios entre requests
- [ ] VisionFallback implementado (requiere Ollama para funcionar)
- [ ] TextParser implementado (requiere Ollama para funcionar)
- [ ] ProductMatcher por aliases funciona sin Ollama
- [ ] DataValidator valida rangos de precios/fees/tiempos
- [ ] DataMerger genera CSV con 24 columnas

## Seguridad

- [ ] No hay secrets en el codigo
- [ ] .env no esta en git
- [ ] data/raw/, data/merged/, data/screenshots/ en .gitignore
