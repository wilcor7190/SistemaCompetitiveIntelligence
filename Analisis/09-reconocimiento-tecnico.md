# 09 - Reconocimiento Tecnico: Spike de las 3 Plataformas

## Resumen Ejecutivo

| Plataforma | Version Web? | Precios sin login? | Fees visibles? | Tiempo entrega? | Scrapeabilidad |
|------------|-------------|-------------------|----------------|-----------------|----------------|
| **Uber Eats** | SI, SPA completa | SI | Delivery: $4.99 MXN | Necesita direccion | ALTA |
| **Rappi** | SI, PWA completa | SI | Envio gratis (promo) | 35 min visible | ALTA |
| **DiDi Food** | SI, SPA pero pesada | Por verificar | Por verificar | Por verificar | MEDIA-BAJA |

---

## Uber Eats (ubereats.com/mx) - MEJOR CANDIDATO

### Hallazgos

- **URL funcional:** `ubereats.com/mx/store/{restaurante}/{id}`
- **Tecnologia:** React + Next.js, SPA con rendering JS
- **Login:** NO requerido para ver menus y precios
- **Direccion:** Se puede ingresar sin cuenta. Necesaria para ver tiempos de entrega, NO para precios
- **Anti-bot:** Tiene botdefense, reCAPTCHA, Arkose. Riesgo MEDIO-ALTO
- **Idioma:** Espanol Mexico nativo

### Datos Verificados (McDonald's Polanco)

```
Producto              Precio MXN
─────────────────────────────────
Big Mac               $145.00
McTrio Hamb c/Queso   $95.00
McTrio Hamb Dbl       $105.00
McNuggets 4 pzas      $59.00
McNuggets 10 pzas     $155.00
McNuggets 20 pzas     $209.00
Papas grandes         $79.00
McPollo               $89.00
McFlurry Oreo         $59.00
Coca-Cola mediana      $65.00
Hamburguesa c/Queso   $59.00

Delivery Fee:          $4.99 MXN
Service Fee:           No visible en pagina (se muestra en checkout)
Tiempo entrega:        Requiere direccion
Rating:                4.5/5 (25,000+ resenas)
Horario:               12:00-23:59, 00:00-05:45, 07:00-11:45
```

### URLs Descubiertas

```
Pagina principal:     ubereats.com/mx
Buscar restaurante:   ubereats.com/mx/brand-city/mexico-city-df/mcdonalds
Tienda especifica:    ubereats.com/mx/store/mcdonalds-polanco/GMcH3w_vX4CtLxBPRICeWA
Tienda Reforma:       ubereats.com/mx/store/mcdonalds-reforma/yD_69FtxTTGWjKm4rJ1BEg
```

### Estrategia de Scraping

```
CAPA 1 (preferida): API Interception
  - React SPA = todas las llamadas pasan por APIs internas
  - Interceptar con Playwright page.on('response')
  - Buscar endpoints tipo /api/getStoreV1 o similar

CAPA 2 (fallback): DOM Parsing
  - Precios estan en el DOM una vez carga JS
  - Selectores CSS a descubrir con DevTools
  - Requiere headless browser con JS rendering

CAPA 3 (backup): Screenshot + OCR
  - Pagina se renderiza visualmente bien
  - qwen3-vl puede leer precios de screenshot
```

### Riesgo Principal
Anti-bot (botdefense/Arkose). Puede requerir stealth + proxies.

---

## Rappi (rappi.com.mx) - BUEN CANDIDATO

### Hallazgos

- **URL funcional:** `rappi.com.mx/restaurantes/{id}-{nombre}`
- **Tecnologia:** Next.js + Styled Components + Chakra UI + i18next
- **Login:** NO requerido para ver menus y precios
- **Direccion:** Tiene campo "Donde quieres recibir tu compra?" pero precios se ven sin ella
- **Anti-bot:** reCAPTCHA presente. Riesgo MEDIO
- **Tipo:** PWA (Progressive Web App) hibrida, funciona completa en browser

### Datos Verificados (McDonald's Alvaro Obregon)

```
Producto                     Precio MXN
──────────────────────────────────────────
Big Mac Tocino               $155.00
McTrio mediano Big Mac Tocino $179.00
McTrio Hamb c/Queso          $95.00
Cajita Feliz Hamburguesa     $139-149.00
McNuggets 10 pzas            $145.00
McFlurry Oreo                $59.00
Papas grandes                $75.00

Delivery Fee:          Envio Gratis (promo nuevos usuarios)
Service Fee:           No visible en pagina de restaurante
Tiempo entrega:        35 min
Promociones:           "Hasta 64% OFF imperdible", "Envio gratis"
Rating:                4.1/5
```

### URLs Descubiertas

```
Pagina principal:     rappi.com.mx
Restaurante:          rappi.com.mx/restaurantes/1306705702-mcdonalds
Otros McDonalds:      rappi.com.mx/restaurantes/1306705685-mcdonalds (Centro)
                      rappi.com.mx/restaurantes/1306718166-mcdonalds (Juarez)
                      rappi.com.mx/restaurantes/1923200225-mcdonalds (Supmz 7)
```

### Estrategia de Scraping

```
CAPA 1 (preferida): API Interception
  - Next.js = hace fetch a APIs para datos de restaurantes
  - Buscar endpoints tipo /_next/data/ o /api/
  - Probablemente GraphQL o REST interno

CAPA 2 (fallback): DOM Parsing
  - Precios visibles en DOM sin login
  - Next.js server-renders algo de contenido = posible sin JS?
  - Styled Components = selectores CSS pueden ser dinamicos (hash)

CAPA 3 (backup): Screenshot + OCR
  - Interfaz limpia, precios legibles
  - qwen3-vl puede leer facilmente
```

### Riesgo Principal
Selectores CSS dinamicos (Styled Components genera class names con hash). API interception es preferible.

### Hallazgo Importante: Diferencia de Precios con Uber Eats

```
Producto         Uber Eats    Rappi       Diferencia
─────────────────────────────────────────────────────
McNuggets 10pz   $155.00     $145.00     Rappi -6.5%
McTrio Hamb QQ    $95.00      $95.00     Igual
Papas grandes     $79.00      $75.00     Rappi -5.1%
McFlurry Oreo     $59.00      $59.00     Igual
```

Esto YA es un insight potencial solo con datos del spike.

---

## DiDi Food (didi-food.com) - CANDIDATO DIFICIL

### Hallazgos

- **URL principal:** `didi-food.com/es-MX/food/`
- **URL tienda:** `didi-food.com/es-MX/food/store/{id}/{nombre}/`
- **Tecnologia:** SPA con JS vanilla (no React/Next.js visible), pesada en JS
- **Login:** Tiene login-wrapper con z-index alto, posiblemente requerido
- **Direccion:** Requiere direccion almacenada (localStorage 'pl') para ver el feed
- **Anti-bot:** Menos sofisticado que Uber/Rappi pero SPA muy dependiente de JS
- **Estado en Mexico:** Activo, crecio 19% en restaurantes en 2025, 30M+ usuarios, 60+ ciudades

### Datos Verificados

```
NO SE PUDIERON VERIFICAR PRECIOS desde el fetch estatico.
La pagina requiere:
  1. JavaScript habilitado (SPA pura)
  2. Posiblemente una direccion guardada en localStorage
  3. Posible login

El mensaje sin JS: "We're sorry but b_c_i18n doesn't work properly
without JavaScript enabled"
```

### URLs Descubiertas

```
Home:           didi-food.com/es-MX/food/
Feed:           didi-food.com/es-MX/food/feed/
Direccion:      didi-food.com/es-MX/food/address
Tienda ejemplo: didi-food.com/es-MX/food/store/{id}/{nombre}/
PC version:     didi-food.com/es-MX/store/pc/home
Developer:      developer.didi-food.com (tiene API publica?)
```

### Estrategia de Scraping

```
CAPA 1: API Interception (UNICA VIABLE)
  - SPA pura = TODO pasa por APIs
  - Interceptar con Playwright es la unica forma confiable
  - developer.didi-food.com sugiere que hay APIs documentadas

CAPA 2: DOM Parsing
  - MUY DIFICIL: SPA sin server-rendering
  - Selectores CSS probablemente dinamicos
  - Requiere esperar carga completa + posible login

CAPA 3: Screenshot + OCR (PLAN B FUERTE)
  - Si Capa 1 y 2 fallan, screenshots son la opcion
  - Requiere navegar manualmente o con browser automation
  - qwen3-vl extrae datos de la imagen
```

### Riesgo Principal
Es la plataforma mas dificil de scrapear. Si hay bloqueo temporal, vale la pena considerar:

**Alternativa:** Si DiDi Food es demasiado dificil, podemos sustituir por otro competidor que tenga mejor version web. El brief dice "al menos 2 competidores + Rappi". Opciones:

| Alternativa | Dificultad | Presencia Mexico |
|-------------|------------|-----------------|
| DiDi Food | Alta | Si (60+ ciudades) |
| Cornershop (Uber) | Media | Si (ya es parte de Uber) |
| Sin Delantal | Baja | Si pero menor |

---

## Hallazgos Criticos para el Diseno

### 1. Service Fee NO es visible en la pagina del restaurante

En **ninguna** de las 3 plataformas el service fee es visible en la pagina del restaurante. Solo aparece en el checkout (carrito). Esto significa:

```
IMPLICACION: Para obtener service fee necesitamos:
  Opcion A: Agregar producto al carrito y leer el checkout
  Opcion B: Interceptar la API del checkout
  Opcion C: Documentar que service fee no es accesible sin compra

Recomendacion: Documentar como limitacion, enfocarse en las otras metricas.
El brief dice "minimo 3 metricas". Tenemos:
  1. Precio producto ✓ (visible en todas)
  2. Delivery fee ✓ (visible en Uber Eats, parcial en Rappi)
  3. Tiempo entrega ✓ (visible en Rappi, requiere direccion en Uber)
  4. Promociones ✓ (visibles en Rappi)
  5. Disponibilidad ✓ (si el restaurante aparece = disponible)
```

### 2. Los precios YA varian entre plataformas

Solo con el spike encontramos diferencias:
- McNuggets 10: $155 (Uber Eats) vs $145 (Rappi) = **6.5% mas caro en Uber**
- Papas grandes: $79 (Uber) vs $75 (Rappi) = **5.1% mas caro en Uber**

Esto valida que el sistema tiene razon de ser. Hay insights reales en los datos.

### 3. McDonald's tiene multiples sucursales por zona

Cada plataforma lista McDonald's por sucursal, no como marca unica. Necesitamos:
- Buscar la sucursal **mas cercana a cada direccion** (no una fija)
- O buscar por marca y tomar la primera disponible

### 4. La estructura de URLs es predecible

```
Uber Eats:  /mx/store/{nombre-slug}/{id-hash}
Rappi:      /restaurantes/{id-numerico}-{nombre-slug}
DiDi Food:  /es-MX/food/store/{id-numerico}/{nombre}/
```

Los IDs de Uber son hashes, los de Rappi/DiDi son numericos. Esto importa para la estrategia de scraping.

### 5. DiDi Food es la mas dificil, considerar alternativa

Si DiDi consume demasiado tiempo, mejor tener 2 plataformas bien scrapeadas que 3 a medias. El brief dice:

> "Prioriza calidad sobre cantidad"

---

## Validacion de Supuestos

| Supuesto Original | Verificado? | Realidad |
|-------------------|-------------|----------|
| Las 3 tienen version web | PARCIAL | Uber y Rappi SI. DiDi tiene pero es SPA pesada |
| Precios visibles sin login | SI para 2/3 | Uber y Rappi SI. DiDi no verificado |
| Delivery fee visible | PARCIAL | Uber: $4.99, Rappi: "gratis" (promo), DiDi: ? |
| Service fee visible | NO | Ninguna lo muestra fuera del checkout |
| McDonald's en las 3 | PROBABLE | Confirmado Uber y Rappi. DiDi probable |
| Precios iguales entre plataformas | NO | Ya hay diferencias de 5-7% |
| Anti-bot es problema | POR VERIFICAR | Uber tiene Arkose, Rappi reCAPTCHA, DiDi desconocido |

---

## Ajustes al Rumbo Estrategico

Con este reconocimiento, ajusto las prioridades:

```
ANTES (supuesto):
  Uber Eats → API interception
  Rappi → Playwright
  DiDi Food → Playwright

AHORA (verificado):
  1. Rappi → EMPEZAR AQUI (precios visibles, PWA completa, menos anti-bot)
  2. Uber Eats → Segundo (precios visibles, mas anti-bot pero mas documentado)
  3. DiDi Food → Ultimo y con Plan B (SPA pesada, posible login, menos info)
     → Si DiDi es muy dificil: pivotar a solo 2 plataformas y documentar

CAMBIO CLAVE: Empezar por Rappi, no por Uber Eats.
  Razon: Rappi es el baseline propio del caso, y la web es mas accesible.
```

---

## Siguiente Paso

El analisis esta completo. 9 documentos cubren:

```
01 - Que nos piden (requerimiento)
02 - Que existe en el mercado (herramientas)
03 - Que opciones tenemos (enfoques)
04 - Como segmentar en MVPs (roadmap)
05 - Como se ve la arquitectura (propuesta)
06 - Que tecnologias elegir (decisiones)
07 - Que modelos de IA usar (Ollama)
08 - Que rumbo tomar (estrategia)
09 - Que encontramos al explorar las plataformas (ESTE)
```

Fase de analisis cerrada. Listos para pasar a diseno/.
