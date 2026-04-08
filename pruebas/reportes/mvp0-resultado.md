# Reporte de Resultado — MVP 0: PoC Rappi

**Fecha de ejecucion:** ____-__-__
**Branch:** feature/poc-rappi
**Ejecutado por:** _______________

---

## Tests Automatizados

| Suite | Tests | Pasados | Fallidos | Tiempo |
|-------|-------|---------|----------|--------|
| test_models.py | __ | __ | __ | __s |
| test_config.py | __ | __ | __ | __s |
| **TOTAL** | **__** | **__** | **__** | **__s** |

Comando: `cd desarrollo && pytest tests/ -v`

### Output de pytest
```
[Pegar output aqui]
```

---

## Test Manual: CLI --debug

**Comando:** `cd desarrollo && python -m src.main --debug`

### Observaciones
- Browser abrio: Si / No
- URL navegada: _______________
- Datos extraidos: Si / No
- Exit code: ___

### JSON de salida
```json
[Pegar JSON aqui]
```

---

## Datos Obtenidos

| Metrica | Valor |
|---------|-------|
| Plataforma | Rappi |
| Direccion | Reforma 222 - Centro Historico |
| Tienda | McDonald's |
| Items extraidos | __ |
| Layer utilizado | api / dom / vision / ninguno |
| Delivery fee | __ |
| Tiempo estimado | __ |
| Success | True / False |
| Duracion scraping | __s |

---

## Problemas Encontrados

| # | Problema | Severidad | Resolucion |
|---|----------|-----------|------------|
| 1 | ___________ | Alta/Media/Baja | ___________ |

---

## Screenshots / Evidencia

- [ ] Screenshot de consola con output del scraper
- [ ] Screenshot de browser navegando a Rappi (si headless=false)
- [ ] JSON de salida guardado

---

## Conclusion

_[Resumen: el PoC funciono? Que capa se uso? Que ajustes se necesitan para MVP 1?]_

### Decision de corte (del plan-mvps.md)
- [ ] Capa 1 (API) funciono → seguir con MVP 1
- [ ] Capa 2 (DOM) funciono → seguir con MVP 1
- [ ] Capa 3 (Vision) funciono → seguir, ajustar expectativas
- [ ] Las 3 capas fallaron → debuggear antes de MVP 1
