# Guia: Como agregar una nueva tienda, sucursal o plataforma

Esta guia te explica paso a paso como extender el sistema sin tocar el codigo
existente (en la mayoria de los casos).

---

## Caso 1: Agregar una nueva direccion (sucursal donde scrapear)

**Tiempo:** 2 minutos
**Archivos a modificar:** 1
**Codigo nuevo:** 0

### Pasos

1. Abre `desarrollo/config/addresses.json`
2. Agrega un objeto al array `addresses`:

```json
{
  "label": "Mi Nueva Sucursal - Colonia",
  "lat": 19.4326,
  "lng": -99.1332,
  "zone_type": "centro",
  "city": "CDMX",
  "full_address": "Calle Falsa 123, Colonia, 06000 CDMX"
}
```

3. **Tipos de zona validos** (debe ser uno de estos):
   - `centro`
   - `premium`
   - `residencial`
   - `periferia`
   - `corporativo`
   - `expansion`

4. Guarda el archivo. **Listo.** El sistema lo recogera automaticamente en la siguiente ejecucion.

### Probarlo

```bash
cd desarrollo
source venv/Scripts/activate
python -m src.main --platforms rappi --max-addresses 1 --headless
```

---

## Caso 2: Agregar un nuevo producto a buscar

**Tiempo:** 2 minutos
**Archivos a modificar:** 1
**Codigo nuevo:** 0

### Pasos

1. Abre `desarrollo/config/products.json`
2. Encuentra el `store_group` correcto (`restaurant`, `convenience`, o `pharmacy`)
3. Agrega un objeto al array `products`:

```json
{
  "canonical_name": "McFlurry Oreo",
  "aliases": [
    "mcflurry oreo",
    "mc flurry oreo",
    "mcflurry de oreo",
    "helado oreo"
  ],
  "category": "fast_food",
  "expected_price_range": {"min": 30, "max": 100},
  "notes": "Postre helado con galletas Oreo"
}
```

### Tips para los aliases

Los aliases son **CRITICOS** para que el matcher encuentre el producto.
Incluye:
- Variaciones ortograficas (con y sin guion)
- Errores comunes ("mac" vs "mc")
- Sinonimos y descripciones alternativas
- Como aparece literalmente en cada plataforma (cada una usa nombres distintos)

### Probarlo

```bash
python -m src.main --debug
# Verificar en el output que el matcher encuentra el nuevo producto
```

---

## Caso 3: Agregar una nueva cadena (ej: Burger King en lugar de McDonald's)

**Tiempo:** 5-10 minutos
**Archivos a modificar:** 2
**Codigo nuevo:** Posiblemente actualizar URLs en el scraper

### Pasos

1. **Agregar productos nuevos a `products.json`** (si son diferentes a los actuales):

```json
{
  "store_type": "restaurant",
  "store_name": "Burger King",
  "store_aliases": ["burger king", "bk", "burgerking"],
  "products": [
    {
      "canonical_name": "Whopper",
      "aliases": ["whopper", "whopper clasica"],
      "category": "fast_food",
      "expected_price_range": {"min": 100, "max": 200}
    }
  ]
}
```

2. **Descubrir las URLs reales** abriendo la plataforma con DevTools:
   - Para Rappi: `rappi.com.mx/restaurantes/{ID}-burger-king`
   - Para Uber Eats: `ubereats.com/mx/store/burger-king-xxx/{HASH}`

3. **Actualizar el scraper** correspondiente. En `desarrollo/src/scrapers/rappi.py`:

```python
# Cerca del inicio del archivo
BURGER_KING_STORE_IDS = [
    "1234567890",  # ID descubierto en DevTools
]

# En el metodo _navigate_to_restaurant, agregar logica:
async def _navigate_to_restaurant(self, name: str | None) -> bool:
    if name and "burger" in name.lower():
        store_id = BURGER_KING_STORE_IDS[0]
        url = f"{self.BASE_URL}/restaurantes/{store_id}-burger-king"
    else:
        # Default: McDonald's
        store_id = MCDONALDS_STORE_IDS[0]
        url = f"{self.BASE_URL}/restaurantes/{store_id}-mcdonalds"
    return await self._goto_store(url, store_id)
```

4. **Probar:**

```bash
python -m src.main --debug
```

---

## Caso 4: Agregar una nueva plataforma (ej: Pedidos Ya, Domicilios)

**Tiempo:** 4-8 horas (depende de la complejidad de la plataforma)
**Archivos a modificar:** 4
**Codigo nuevo:** ~200-400 lineas

### Paso 1: Agregar el enum

`desarrollo/src/models/schemas.py`:

```python
class Platform(str, Enum):
    RAPPI = "rappi"
    UBER_EATS = "uber_eats"
    DIDI_FOOD = "didi_food"
    PEDIDOS_YA = "pedidos_ya"  # nuevo
```

### Paso 2: Crear el scraper

Crea `desarrollo/src/scrapers/pedidos_ya.py` siguiendo el patron de los existentes:

```python
"""PedidosYaScraper: scraper for pedidosya.com.mx."""

import re
from playwright.async_api import TimeoutError as PlaywrightTimeout

from src.config import ScraperConfig
from src.models.schemas import (
    Address, FeeInfo, Platform, ScrapedItem, StoreType, TimeEstimate,
)
from src.scrapers.base import BaseScraper

PEDIDOS_YA_SELECTORS = {
    "product_card": "...",  # descubrir con DevTools
    "product_name": "...",
    "product_price": "...",
    # etc
}


class PedidosYaScraper(BaseScraper):
    BASE_URL = "https://www.pedidosya.com.mx"

    def __init__(self, config: ScraperConfig):
        super().__init__(config, Platform.PEDIDOS_YA)

    def get_base_url(self) -> str:
        return self.BASE_URL

    def get_platform_selectors(self) -> dict[str, str]:
        return PEDIDOS_YA_SELECTORS

    async def set_address(self, address: Address) -> bool:
        # Implementar segun como Pedidos Ya maneja direcciones
        return True

    async def search_store(self, store_type, store_name) -> bool:
        # Navegar a McDonald's en Pedidos Ya
        url = f"{self.BASE_URL}/restaurantes/mcdonalds"
        await self.page.goto(url)
        return True

    async def extract_items(self, product_names: list[str]) -> list[ScrapedItem]:
        # Extraer productos del DOM
        return []

    async def extract_fees(self) -> FeeInfo:
        return FeeInfo()

    async def extract_delivery_time(self) -> TimeEstimate:
        return TimeEstimate()
```

### Paso 3: Registrar el scraper en el orchestrator

`desarrollo/src/scrapers/orchestrator.py`:

```python
from src.scrapers.pedidos_ya import PedidosYaScraper

def _create_scraper(self, platform: Platform) -> BaseScraper | None:
    if platform == Platform.RAPPI:
        return RappiScraper(self.scraper_config)
    if platform == Platform.UBER_EATS:
        return UberEatsScraper(self.scraper_config)
    if platform == Platform.DIDI_FOOD:
        return DiDiFoodScraper(self.scraper_config)
    if platform == Platform.PEDIDOS_YA:  # nuevo
        return PedidosYaScraper(self.scraper_config)
    return None
```

### Paso 4: Agregar a settings.yaml

`desarrollo/config/settings.yaml`:

```yaml
scraping:
  platforms:
    - rappi
    - uber_eats
    - didi_food
    - pedidos_ya  # nuevo
```

### Paso 5: Descubrir selectores reales

**Esto es la parte mas importante.** Los selectores CSS estimados nunca funcionan en la primera. Para descubrir los reales:

```bash
# Script helper para inspeccionar la pagina
cd desarrollo
source venv/Scripts/activate
python -c "
import asyncio
from playwright.async_api import async_playwright

async def inspect():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto('https://www.pedidosya.com.mx/restaurantes/mcdonalds')
    await page.wait_for_timeout(5000)
    # Toma screenshot para revisar
    await page.screenshot(path='inspection.png')
    # Busca productos con $
    prices = await page.evaluate('''() => {
        const els = document.querySelectorAll('*');
        return Array.from(els)
            .filter(e => e.textContent.match(/\\\$\\\s*\\\d/) && e.children.length === 0)
            .slice(0, 10)
            .map(e => ({
                tag: e.tagName,
                cls: e.className,
                text: e.textContent.trim().substring(0, 50)
            }));
    }''')
    print(prices)
    await browser.close()
    await pw.stop()

asyncio.run(inspect())
"
```

### Paso 6: Tests

Agregar tests en `desarrollo/tests/test_scrapers.py`:

```python
def test_pedidos_ya_scraper_creates(self):
    s = PedidosYaScraper(_make_config())
    assert s.platform == Platform.PEDIDOS_YA
```

### Paso 7: Probar

```bash
python -m src.main --platforms pedidos_ya --debug
```

---

## Caso 5: Cambiar el modelo de Claude (ej: Haiku para ahorrar costos)

**Tiempo:** 1 minuto
**Archivos a modificar:** 1

Edita `desarrollo/src/utils/claude_client.py`:

```python
DEFAULT_MODEL = "claude-haiku-4-5"  # antes: claude-opus-4-6
```

**Comparativa de modelos:**

| Modelo | Precio Input/Output (1M tokens) | Calidad | Velocidad |
|--------|--------------------------------|---------|-----------|
| `claude-opus-4-6` | $5 / $25 | Mejor | Media |
| `claude-sonnet-4-6` | $3 / $15 | Muy buena | Rapida |
| `claude-haiku-4-5` | $1 / $5 | Buena | Muy rapida |

Para insights de calidad VP, recomendado **opus-4-6**.
Para volumen alto y costos bajos, **haiku-4-5**.

---

## Resumen rapido

| Quiero... | Modificar | Tiempo |
|-----------|-----------|--------|
| Nueva direccion | `config/addresses.json` | 2 min |
| Nuevo producto | `config/products.json` | 2 min |
| Nueva cadena | `config/products.json` + scraper existente | 5-10 min |
| Nueva plataforma | Crear scraper nuevo + registrar en orchestrator | 4-8 horas |
| Cambiar modelo Claude | `claude_client.py` linea 14 | 1 min |
