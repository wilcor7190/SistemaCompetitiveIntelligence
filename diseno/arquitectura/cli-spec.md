# CLI Specification — main.py

## Invocacion

```bash
cd desarrollo
python -m src.main [OPTIONS]
```

---

## Argumentos

| Flag | Tipo | Default | Descripcion |
|------|------|---------|-------------|
| `--platforms` | string (csv) | `rappi,uber_eats,didi_food` | Plataformas a scrapear, separadas por coma |
| `--addresses` | path | `config/addresses.json` | Ruta al archivo de direcciones |
| `--products` | path | `config/products.json` | Ruta al archivo de productos |
| `--settings` | path | `config/settings.yaml` | Ruta al archivo de settings |
| `--output-dir` | path | `data/` | Directorio base de salida |
| `--screenshots` | flag | `false` | Capturar screenshots en cada extraccion (no solo en fallos) |
| `--headless` | bool | `true` | Ejecutar browser en modo headless |
| `--debug` | flag | `false` | 1 direccion, 1 plataforma, verbose logging, headless=false |
| `--report-only` | flag | `false` | Saltar scraping, generar reporte desde datos existentes |
| `--report-data` | path | `data/merged/comparison.csv` | CSV a usar con `--report-only` |
| `--save-backup` | flag | `false` | Guardar copia de raw data en `data/backup/` |
| `--use-backup` | flag | `false` | Usar datos pre-scrapeados de `data/backup/` en vez de scrapear |
| `--max-addresses` | int | `0` (all) | Limitar a N direcciones (util para testing) |
| `--dry-run` | flag | `false` | Validar config y mostrar plan de ejecucion sin scrapear |

---

## Combinaciones de Uso Comunes

### Ejecucion completa (produccion)

```bash
python -m src.main
# Usa todos los defaults: 3 plataformas, 25 direcciones, headless
# Output: data/raw/*.json + data/merged/comparison.csv + reports/insights.html
```

### PoC rapido — 1 plataforma, 1 direccion

```bash
python -m src.main --debug
# Equivalente a: --platforms rappi --max-addresses 1 --headless false --logging DEBUG
# Para verificar que funciona antes de un run completo
```

### Solo Rappi con screenshots

```bash
python -m src.main --platforms rappi --screenshots
# Scrapea solo Rappi, captura screenshots de cada pagina
```

### Solo generar reporte (con datos existentes)

```bash
python -m src.main --report-only
# Lee data/merged/comparison.csv y genera reports/insights.html
# Util cuando ya tienes datos y quieres regenerar insights
```

```bash
python -m src.main --report-only --report-data data/merged/comparison_20260407.csv
# Usa un CSV especifico
```

### Guardar backup para demo

```bash
python -m src.main --save-backup
# Ejecuta scraping normal Y guarda copia en data/backup/
# Para tener datos pre-scrapeados para la presentacion
```

### Usar backup (demo o si scraping falla)

```bash
python -m src.main --use-backup
# Salta scraping, usa datos de data/backup/
# Normalizacion e insights se ejecutan normalmente
```

### Testing con pocas direcciones

```bash
python -m src.main --platforms rappi,uber_eats --max-addresses 3
# Solo 2 plataformas, solo 3 direcciones = 6 scrapes (~1 min)
```

### Dry run (verificar plan sin ejecutar)

```bash
python -m src.main --dry-run
# Output:
# Plan de ejecucion:
#   Plataformas: rappi, uber_eats, didi_food
#   Direcciones: 25 (5 centro, 5 premium, 5 residencial, 5 periferia, 5 corporativo)
#   Productos: 5 (Big Mac, McNuggets 10 pzas, Combo Mediano, Coca-Cola 600ml, Agua Bonafont 1L)
#   Estimacion: ~375 data points, ~15-25 min
#   Ollama: disponible (qwen3-vl:8b, qwen3.5:9b, nomic-embed-text)
#   Config: OK
```

---

## Implementacion con argparse

```python
import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="competitive-intelligence",
        description="Sistema de Competitive Intelligence para delivery platforms en Mexico"
    )
    
    # Scraping options
    parser.add_argument("--platforms", type=str, default="rappi,uber_eats,didi_food",
                        help="Plataformas a scrapear, separadas por coma")
    parser.add_argument("--addresses", type=str, default="config/addresses.json",
                        help="Ruta al archivo de direcciones")
    parser.add_argument("--products", type=str, default="config/products.json",
                        help="Ruta al archivo de productos")
    parser.add_argument("--settings", type=str, default="config/settings.yaml",
                        help="Ruta al archivo de settings")
    parser.add_argument("--max-addresses", type=int, default=0,
                        help="Limitar a N direcciones (0 = todas)")
    
    # Output options
    parser.add_argument("--output-dir", type=str, default="data/",
                        help="Directorio base de salida")
    parser.add_argument("--screenshots", action="store_true",
                        help="Capturar screenshots en cada extraccion")
    
    # Browser options
    parser.add_argument("--headless", type=bool, default=True,
                        help="Ejecutar browser headless")
    
    # Mode shortcuts
    parser.add_argument("--debug", action="store_true",
                        help="Modo debug: 1 plataforma, 1 direccion, verbose, no headless")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar plan de ejecucion sin scrapear")
    
    # Report options
    parser.add_argument("--report-only", action="store_true",
                        help="Solo generar reporte desde datos existentes")
    parser.add_argument("--report-data", type=str, default="data/merged/comparison.csv",
                        help="CSV a usar con --report-only")
    
    # Backup options
    parser.add_argument("--save-backup", action="store_true",
                        help="Guardar copia de datos en data/backup/")
    parser.add_argument("--use-backup", action="store_true",
                        help="Usar datos pre-scrapeados de data/backup/")
    
    return parser

def apply_debug_overrides(args):
    """Cuando --debug esta activo, sobreescribir settings para PoC rapido."""
    if args.debug:
        args.platforms = "rappi"
        args.max_addresses = 1
        args.headless = False
        # logging level se sube a DEBUG en Config
```

---

## Flujo de main.py

```
1. Parse arguments
2. Si --debug: aplicar overrides
3. Si --dry-run: cargar config, mostrar plan, salir
4. Cargar Config(settings, addresses, products)
5. Validar Ollama disponible (warning si no)
6. Si --use-backup: cargar datos de data/backup/, saltar a paso 9
7. Si --report-only: cargar CSV, saltar a paso 10
8. ScrapingOrchestrator.run_all() → raw JSONs
9. DataNormalizer + DataMerger → comparison.csv
10. Si --save-backup: copiar raw data a data/backup/
11. InsightGenerator.generate() → 5 insights
12. Visualizations.generate() → charts/
13. ReportGenerator.generate() → insights.html
14. Imprimir resumen a consola
```

---

## Exit Codes

| Code | Significado |
|------|-------------|
| `0` | Exito completo |
| `1` | Error de configuracion (archivo no encontrado, YAML invalido) |
| `2` | Ollama no disponible (warning, no fatal si solo capas 1-2 funcionan) |
| `3` | Scraping fallo completamente (0 datos de todas las plataformas) |
| `4` | Error generando reporte |
