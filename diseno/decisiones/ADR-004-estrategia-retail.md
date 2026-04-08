# ADR-004: Estrategia de Productos Retail (Multi-Store Scraping)

**Estado:** Aceptado  
**Fecha:** 2026-04-07

## Contexto

El brief pide productos de referencia que incluyen 2 categorias distintas:

```
FAST FOOD (restaurante):    Big Mac, Combo Mediano, McNuggets 10 pzas
RETAIL (tienda/farmacia):   Coca-Cola 600ml, Agua Bonafont 1L, Panales
```

El diseno original asumia que todos los productos se buscaban en **McDonald's**. Esto es incorrecto:
- Coca-Cola 600ml, Agua Bonafont 1L y Panales NO se venden en McDonald's via delivery
- Estos productos se encuentran en **tiendas de conveniencia** (Oxxo, 7-Eleven) o **la seccion de retail/turbo** de cada plataforma
- El brief intencionalmente mezcla categorias para evaluar si el sistema maneja **multiples verticales**

### Contexto por Plataforma

| Plataforma | Restaurantes | Retail/Tienda | Farmacia |
|------------|-------------|---------------|----------|
| **Rappi** | `/restaurantes/` | Rappi Turbo, Tiendas, Supermercados | Rappi Farmacia |
| **Uber Eats** | `/store/` (restaurantes) | Convenience stores (Oxxo, 7-Eleven) | Farmacias del Ahorro |
| **DiDi Food** | `/store/` | Tiendas de conveniencia | Por verificar |

## Decision

**Extender el sistema para soportar 2 contextos de busqueda: restaurante y tienda.**

### Modelo: SearchContext

```python
class StoreType(str, Enum):
    RESTAURANT = "restaurant"    # McDonald's, Burger King, etc.
    CONVENIENCE = "convenience"  # Oxxo, 7-Eleven, tiendas
    PHARMACY = "pharmacy"        # Farmacias (solo para Panales)
```

Cada producto en `products.json` declara en que tipo de tienda buscarlo:

```json
{
  "canonical_name": "Big Mac",
  "store_type": "restaurant",
  "store_name": "McDonald's"
}
```
```json
{
  "canonical_name": "Coca-Cola 600ml",
  "store_type": "convenience",
  "store_name": "Oxxo"
}
```
```json
{
  "canonical_name": "Panales",
  "store_type": "pharmacy",
  "store_name": null
}
```

### Impacto en el Flujo de Scraping

```
ANTES (1 contexto):
  Para cada direccion:
    1. Navegar a McDonald's
    2. Buscar 5 productos
    
AHORA (2-3 contextos):
  Para cada direccion:
    1. Navegar a McDonald's → buscar Big Mac, Combo, McNuggets
    2. Navegar a Oxxo/retail → buscar Coca-Cola, Agua
    3. Navegar a farmacia/retail → buscar Panales
```

### Impacto en BaseScraper

```python
# ANTES:
async def scrape_address(self, address, products):
    await self.search_restaurant("McDonald's")
    items = await self.extract_items(products)

# AHORA:
async def scrape_address(self, address, product_groups):
    all_items = []
    for store_type, store_name, products in product_groups:
        await self.search_store(store_type, store_name)
        items = await self.extract_items(products)
        all_items.extend(items)
    return all_items
```

El metodo abstracto cambia de `search_restaurant(name)` a `search_store(store_type, store_name)`.

## Alternativas Consideradas

### A. Buscar todo en McDonald's (RECHAZADA)
- **Contra:** Coca-Cola, Agua y Panales no estan en McDonald's delivery
- **Contra:** El evaluador nota que los productos retail no fueron buscados

### B. Ignorar productos retail, solo fast food (RECHAZADA)
- **Pro:** Mas simple, menos codigo
- **Contra:** El brief los lista explicitamente, ignorarlos es no cumplir el requerimiento
- **Contra:** Perdemos el bonus de "multiples verticales"

### C. Buscar en la seccion retail/turbo de cada plataforma (ACEPTADA)
- **Pro:** Cumple el brief completo
- **Pro:** Demuestra capacidad multi-vertical (bonus del brief)
- **Pro:** Mas data points para insights (precios retail vs fast food)
- **Contra:** Mas complejidad: 2-3 stores por direccion en vez de 1
- **Mitigacion:** El flujo es el mismo, solo cambia la navegacion

### D. Tienda especifica (solo Oxxo) para retail (VARIANTE ACEPTADA)
- Para MVP 0-1: hardcodear Oxxo como tienda de retail
- Para MVP 2+: buscar "Coca-Cola" en el search general y tomar la primera tienda
- Panales: buscar en la primera farmacia disponible, o en Rappi Turbo que agrupa todo

## Consecuencias

### Positivas
- **Cobertura completa:** 6 productos en 3 categorias = cumple brief
- **Bonus multi-vertical:** "Mi sistema scrapea restaurantes, tiendas Y farmacias"
- **Mas insights:** Comparar markup de retail vs fast food es un insight potente
- **Narrativa fuerte:** "Rappi cobra 20% mas por una Coca-Cola que Uber Eats via Oxxo"

### Negativas
- **Mas tiempo por direccion:** 2-3 stores en vez de 1 (~+50% tiempo de scraping)
- **Mitigacion:** settings.yaml ya contempla el timing, y el delay beneficia anti-detection
- **Mas selectores:** Cada plataforma tiene selectores diferentes para restaurantes vs retail
- **Mitigacion:** Misma estructura BaseScraper, solo diferente navegacion

### Decision de Corte

```
MVP 0: Solo McDonald's (3 productos fast food). Validar que el sistema funciona.
MVP 1: Agregar Oxxo/retail (Coca-Cola + Agua). Validar multi-store.
MVP 2: Agregar farmacia (Panales) si hay tiempo. Si no, documentar como limitacion.
       Panales es el mas prescindible: el brief dice "minimo 3 metricas", 
       no "todos los productos". 5 de 6 productos = 83% cobertura.
```

### Tiendas Target por Plataforma

| Plataforma | Restaurante | Retail/Convenience | Farmacia |
|------------|------------|-------------------|----------|
| **Rappi** | McDonald's (ID: 1306705702) | Oxxo o Rappi Turbo | Rappi Farmacia |
| **Uber Eats** | McDonald's Polanco (hash: GMcH3w...) | Oxxo o 7-Eleven | Farmacias del Ahorro |
| **DiDi Food** | McDonald's (por descubrir) | Oxxo o tienda cercana | Por verificar |
