# Checklist: MVP 2 — Multi-Platform

**Fecha:** ____-__-__
**Branch:** feature/multi-platform
**Tag:** v0.2.0

---

## Automatizados

- [ ] `pytest tests/ -v` pasa 100% (111 tests)
- [ ] `ruff check src/` sin errores

## Manuales

- [ ] `python -m src.main --platforms rappi --max-addresses 1 --headless` ejecuta OK
- [ ] `python -m src.main --platforms uber_eats --max-addresses 1 --headless` ejecuta OK
- [ ] `python -m src.main --platforms didi_food --max-addresses 1 --headless` ejecuta OK (o documenta fallo)
- [ ] `python -m src.main --max-addresses 1 --headless` (3 plataformas) ejecuta OK

## Datos

- [ ] CSV tiene datos de al menos 2 plataformas
- [ ] Mismo producto aparece en >=2 plataformas para comparacion
- [ ] Scraper factory crea el scraper correcto por plataforma

## Seguridad

- [ ] No hay secrets en el codigo
- [ ] Arkose detection no intenta resolver CAPTCHA
