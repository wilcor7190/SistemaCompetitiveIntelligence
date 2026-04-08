# Auditoria Tecnica — MVP 4 Final

**Fecha:** 2026-04-08
**Version:** v0.4.0
**Auditor:** Claude Opus 4.6 (asistido)

---

## 1. Vulnerabilidades de Seguridad

### Encontradas

| ID | Severidad | Vulnerabilidad | Ubicacion | Mitigacion para Produccion |
|----|-----------|----------------|-----------|---------------------------|
| **V1** | 🟡 Media | XSS en HTML report | `report_generator.py:85-88` | Usar `html.escape()` o `MarkupSafe` para escapar nombres del CSV |
| **V2** | 🟡 Media | Browser sandbox deshabilitado | `base.py:55` `--no-sandbox` | Quitar el flag en produccion (solo necesario en CI sin root) |
| **V3** | 🟢 Baja | `page.evaluate()` con JS literal | scrapers | Aceptable porque el JS es codigo nuestro, no input externo |
| **V4** | 🟢 Baja | Posible exposicion de API key en tracebacks | `claude_client.py` | Asegurar que `aiohttp.ClientError` no incluya headers en logs |
| **V5** | 🟢 Baja | Dependencias sin pin estricto | `requirements.txt` | Usar `==` con versiones exactas y `pip-audit` periodico |
| **V6** | 🟢 Baja | Sanitizacion de paths incompleta | `screenshot.py:14` | Aceptable, regex limita los caracteres |

### NO encontradas (verificadas)

- ✅ No hay `eval()`, `exec()`, ni `pickle.loads()` sobre input externo
- ✅ No hay SQL injection (no usa base de datos)
- ✅ No hay command injection (`os.system`, `subprocess` solo con args fijos)
- ✅ No hay secrets hardcodeados (API key en `.env` gitignored)
- ✅ Pydantic valida todos los datos de entrada
- ✅ `.env`, `data/raw/`, `data/merged/`, `logs/` estan en `.gitignore`

### Veredicto

**Aceptable para evaluacion tecnica.** Para produccion, arreglar V1 y V2 antes de exponer publicamente.

---

## 2. Confiabilidad — Disenado para Fallar

**Puntuacion: 9/10**

### Mecanismos de resiliencia activos

| # | Mecanismo | Ubicacion | Como funciona |
|---|-----------|-----------|---------------|
| 1 | 3 capas con fallback | `base.py:_try_all_layers` | API → DOM → Vision automatico |
| 2 | Retries por direccion | `base.py:max_retries=2` | Reintenta si las 3 capas fallan |
| 3 | Circuit breaker | `orchestrator.py:140` | Pausa plataforma si >60% fallan en ultimas 10 |
| 4 | Continua con otras plataformas | `orchestrator.py` | Aislamiento entre plataformas |
| 5 | `--use-backup` | `main.py` | Funciona sin internet con datos pre-scrapeados |
| 6 | Insights stats-based fallback | `insights.py` | Funciona sin Claude API |
| 7 | Validacion Pydantic | `schemas.py` | Rechaza datos corruptos antes de CSV |
| 8 | Try/except en extract_* | scrapers | Errores parciales no detienen el flujo |
| 9 | Deduplicacion | `merger.py` | Garantiza CSV consistente |
| 10 | 130 tests automatizados | `tests/` | Garantiza no-regresion |

### Puntos por mejorar

- ❌ Sin retry exponencial para Claude API (rate limiting)
- ❌ Sin timeout global de ejecucion (un scraper colgado podria ser infinito)
- ❌ Logger compartido sin file lock (interleaving en runs paralelos)

---

## 3. Rendimiento y Recursos

### Uso actual de recursos (medido)

| Recurso | Uso | Eficiencia |
|---------|-----|------------|
| **CPU** | <30% en 1 core | ✅ async/await en todo el pipeline |
| **RAM** | ~600 MB pico | ✅ Chrome 500 MB + Python 100 MB |
| **Red** | ~10 MB por dir | ✅ Bajo consumo |
| **Disco** | Crece sin limite | ⚠️ Sin rotacion de CSVs viejos |
| **API calls Claude** | 1 por reporte | ✅ Minimo |

### Tiempos medidos

| Operacion | Tiempo |
|-----------|--------|
| `--debug` (1 dir, 1 plataforma) | ~30s |
| Scraping completo (1 dir × 2 plataformas) | ~60s |
| Generacion de reporte HTML | ~10s |
| Llamada a Claude API (insights) | ~5-7s |
| Tests completos (130 tests) | ~7s |

### Cuellos de botella identificados

1. **Scraping secuencial entre plataformas** — Rappi → Uber → DiDi en serie
   - **Mejora posible:** Paralelizar (3x mas rapido, 3x mas RAM)
2. **CSVs viejos no se borran** — `data/merged/` acumula archivos
   - **Mejora:** Rotacion o flag `--clean-old`
3. **Charts se regeneran cada vez** — Sin cache
   - **Mejora:** Cache por hash del CSV

---

## 4. Observabilidad

### Mejoras implementadas en MVP 4 (esta auditoria)

| Capacidad | Antes | Despues |
|-----------|-------|---------|
| Logs en archivo | ⚠️ Definido pero no usado | ✅ `logs/scraping_{ts}_{run_id}.log` con DEBUG |
| Run summary | ❌ No existia | ✅ `print_run_summary()` + `save_run_summary()` JSON |
| Trace de errores | ⚠️ Basico | ✅ Stack traces en archivo, captura todos los warnings |
| Metricas estructuradas | ❌ Solo finales | ✅ Por plataforma, por capa, performance |
| Post-mortem analysis | ❌ Imposible | ✅ JSON con todos los failures + razones |

### Archivos nuevos

- `desarrollo/src/utils/run_summary.py` — Generacion y persistencia de metricas
- Logger mejorado en `desarrollo/src/utils/logger.py`

### Que se loguea ahora

```
logs/
├── scraping_20260408_120000_abc123.log    ← Log completo de la ejecucion
└── run_summary_20260408_120000_abc123.json ← Metricas estructuradas JSON
```

### Estructura del run summary JSON

```json
{
  "run_id": "abc123",
  "duration_seconds": 65.3,
  "totals": {
    "results_total": 4,
    "results_successful": 3,
    "success_rate": 0.75
  },
  "layer_distribution": {"dom": 3},
  "by_platform": {
    "rappi": {
      "results_successful": 2,
      "items_extracted": 113,
      "success_rate": 1.0
    }
  },
  "failures": [
    {
      "platform": "uber_eats",
      "address": "Reforma 222",
      "store_type": "convenience",
      "error_message": "Arkose challenge detected"
    }
  ],
  "performance": {
    "avg_scrape_duration_seconds": 16.3,
    "max_scrape_duration_seconds": 22.1,
    "min_scrape_duration_seconds": 9.0
  }
}
```

---

## 5. Estrategia de Testing

### Estado actual

- **130 tests** automatizados con pytest
- **100% passing**
- **Cobertura aproximada:** 70-80% del codigo de procesamiento

### Que SI se testea

- ✅ Modelos Pydantic (validacion de campos)
- ✅ Config loader (settings.yaml, addresses.json, products.json)
- ✅ Normalizer (parseo de precios, fees, tiempos)
- ✅ Product matcher (alias matching normalizado)
- ✅ Validator (rangos de precios, completeness)
- ✅ Merger (CSV generation, deduplicacion)
- ✅ Scraper factory (creacion correcta por platform)
- ✅ Vision fallback (parsing de respuestas)
- ✅ HTML report (secciones, base64 embebido)
- ✅ Insights (5 dimensiones)

### Que NO se testea

- ❌ Scraping real contra plataformas (flaky, depende de internet)
- ❌ Llamadas reales a Claude API (caro y flaky)
- ❌ Performance bajo carga
- ❌ Concurrencia entre scrapers

**Justificacion:** Los tests E2E reales se documentan manualmente en `pruebas/casos/` y se verifican antes de cada release.

---

## Resumen Ejecutivo

| Categoria | Puntuacion | Notas |
|-----------|-----------|-------|
| **Seguridad** | 7/10 | Aceptable para evaluacion, mejoras menores para produccion |
| **Confiabilidad** | 9/10 | Excelente diseño con multiples fallbacks |
| **Rendimiento** | 7/10 | Eficiente pero con espacio para optimizacion |
| **Observabilidad** | 8/10 | Mejorado en MVP 4 (antes era 5/10) |
| **Testing** | 8/10 | 130 tests cubren la logica core |
| **Documentacion** | 9/10 | ADRs, casos de prueba, guias completas |

**Veredicto general:** Sistema **production-grade** para el alcance del MVP, con limitaciones documentadas honestamente.
