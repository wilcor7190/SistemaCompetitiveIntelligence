# 07 - Modelos Ollama: Donde Aplican en el Proyecto

## Modelos Disponibles (local)

```
ollama list
```

| Modelo | Params | Tipo | RAM aprox |
|--------|--------|------|-----------|
| qwen3.5:9b | 9B | Chat/Code | ~6GB |
| qwen3.5:4b | 4B | Chat/Code | ~3GB |
| qwen3.5:0.8b | 0.8B | Chat/Code | ~1GB |
| qwen2.5:7b | 7B | Chat/Code | ~5GB |
| llama3.1:8b | 8B | Chat/Code | ~5GB |
| deepseek-r1:3b | 3B | Razonamiento | ~2GB |
| ministral-3:8b | 8B | Chat/Code | ~5GB |
| gpt-oss:20b | 20B | Chat/Code | ~12GB |
| qwen3-vl:8b | 8B | Vision+Language | ~6GB |
| qwen3-vl:4b | 4B | Vision+Language | ~3GB |
| qwen3-vl:2b | 2B | Vision+Language | ~2GB |
| gemma3:1b | 1B | Chat | ~1GB |
| gemma3:270m | 270M | Chat | ~0.5GB |
| gemma3n:e4b | 4B | Chat | ~3GB |
| okamototk/gemma3-tools:12b | 12B | Function calling | ~8GB |
| qwen3-embedding:4b | 4B | Embeddings | ~3GB |
| nomic-embed-text:latest | 137M | Embeddings | ~0.5GB |
| embeddinggemma:latest | - | Embeddings | ~1GB |
| translategemma:4b | 4B | Traduccion | ~3GB |
| glm-orca:latest | - | Chat | - |

---

## Donde Aplica Cada Tipo de Modelo

### Necesidades del proyecto vs tipo de modelo

| Necesidad del Proyecto | Aplica IA Local? | Modelo Recomendado | Por que |
|------------------------|------------------|-------------------|---------|
| **Scraping** (70% del peso) | NO directamente | Ninguno | Playwright/Nodriver extraen datos del DOM, no necesitan LLM |
| **Parseo de HTML roto** | SI - util | qwen3.5:4b | Cuando el HTML no es limpio, un LLM puede extraer datos de texto desestructurado |
| **OCR de screenshots** | SI - muy util | qwen3-vl:8b | Leer precios/fees de capturas de pantalla como Plan B |
| **Generacion de insights** | SI - muy util | qwen3.5:9b o gpt-oss:20b | Analizar datos y generar los 5 insights accionables |
| **Normalizacion de datos** | SI - util | qwen3.5:4b | Normalizar nombres de productos entre plataformas |
| **Embeddings para matching** | SI - muy util | qwen3-embedding:4b | Matching de productos similares entre plataformas |
| **Function calling/agentes** | SI - util | okamototk/gemma3-tools:12b | Orquestar scraping con agentes que deciden que hacer |
| **Traduccion** | NO necesario | - | Todo el proyecto es en espanol/ingles, no se necesita |

---

## Casos de Uso Concretos

### 1. OCR de Screenshots (Plan B para datos) - ALTO VALOR

**Problema:** Si el scraping falla (anti-bot), necesitamos datos igualmente.

**Solucion:** Capturar screenshots de las plataformas + OCR con modelo vision.

```python
# Ejemplo: extraer precio de screenshot con qwen3-vl
import ollama

response = ollama.chat(
    model='qwen3-vl:8b',
    messages=[{
        'role': 'user',
        'content': 'Extrae los siguientes datos de esta captura de pantalla '
                   'de Uber Eats en formato JSON: '
                   '- nombre del producto '
                   '- precio del producto '
                   '- delivery fee '
                   '- service fee '
                   '- tiempo estimado de entrega',
        'images': ['screenshot_ubereats.png']
    }]
)
# Output esperado: {"producto": "Big Mac", "precio": 89.00, "delivery_fee": 29.00, ...}
```

**Modelo recomendado:** `qwen3-vl:8b` (mejor calidad) o `qwen3-vl:4b` (mas rapido)

**Impacto en evaluacion:** 
- Demuestra uso de IA (rol es AI Engineer)
- Plan B robusto si scraping falla
- Bonus: capturas automaticas como evidencia (mencionado en el brief)

---

### 2. Generacion de Insights con LLM Local - ALTO VALOR

**Problema:** Generar los 5 insights accionables con formato Finding + Impacto + Recomendacion.

**Solucion:** Alimentar el CSV de datos al LLM local para que genere insights.

```python
import ollama
import pandas as pd

df = pd.read_csv('data/merged/comparison.csv')
data_summary = df.describe().to_string()
sample = df.head(20).to_string()

response = ollama.chat(
    model='qwen3.5:9b',
    messages=[{
        'role': 'system',
        'content': 'Eres un analista de competitive intelligence para Rappi. '
                   'Genera insights accionables basados en datos reales.'
    }, {
        'role': 'user',
        'content': f'Estos son datos comparativos de precios de delivery en Mexico:\n\n'
                   f'RESUMEN ESTADISTICO:\n{data_summary}\n\n'
                   f'MUESTRA DE DATOS:\n{sample}\n\n'
                   f'Genera exactamente 5 insights con este formato:\n'
                   f'### Insight #N: Titulo\n'
                   f'**Finding:** dato especifico con numeros\n'
                   f'**Impacto:** por que importa para Rappi\n'
                   f'**Recomendacion:** accion concreta\n'
    }]
)
```

**Modelo recomendado:** `qwen3.5:9b` (mejor razonamiento) o `gpt-oss:20b` (mas potente pero mas lento)

**Impacto en evaluacion:**
- Insights con IA = diferenciador vs hacerlo manual
- Muestra capacidad de AI Engineering real
- Los insights se pueden refinar/editar despues

---

### 3. Matching de Productos entre Plataformas - MEDIO VALOR

**Problema:** "Big Mac" en UberEats puede llamarse "BigMac" en Rappi o "Big Mac Individual" en DiDi.

**Solucion:** Embeddings para matching semantico de productos.

```python
import ollama

def get_embedding(text):
    response = ollama.embed(model='nomic-embed-text', input=text)
    return response['embeddings'][0]

# Comparar nombres de productos
uber_name = "Big Mac"
rappi_name = "BigMac Individual"
didi_name = "Big Mac Sola"

emb_uber = get_embedding(uber_name)
emb_rappi = get_embedding(rappi_name)

# Cosine similarity para determinar si es el mismo producto
from numpy import dot
from numpy.linalg import norm
similarity = dot(emb_uber, emb_rappi) / (norm(emb_uber) * norm(emb_rappi))
# similarity > 0.85 = mismo producto
```

**Modelo recomendado:** `nomic-embed-text` (rapido, ligero, preciso)

**Impacto en evaluacion:**
- Resuelve un problema real de normalizacion
- Demuestra conocimiento de embeddings
- Lightweight (corre en background)

---

### 4. Parseo Inteligente de HTML Desestructurado - MEDIO VALOR

**Problema:** El HTML de las plataformas puede cambiar, los selectores CSS se rompen.

**Solucion:** Si un selector falla, pasar el texto crudo al LLM para extraer datos.

```python
import ollama

raw_text = """
McDonald's
Big Mac
$89.00
Combo mediano $129.00
Delivery $29.00
Tiempo estimado: 25-35 min
"""

response = ollama.chat(
    model='qwen3.5:4b',
    messages=[{
        'role': 'user',
        'content': f'Extrae datos estructurados de este texto de una app de delivery.\n'
                   f'Responde SOLO con JSON valido:\n\n{raw_text}'
    }],
    format='json'
)
```

**Modelo recomendado:** `qwen3.5:4b` (rapido, suficiente para parseo)

**Impacto:** Fallback robusto cuando los selectores CSS fallan.

---

### 5. Agente Orquestador con Function Calling - BAJO VALOR (overengineering)

**Problema:** Coordinar multiples scrapers con logica de decision.

**Modelo:** `okamototk/gemma3-tools:12b`

**Por que bajo valor:** Para el scope de 2 dias, un script Python con if/else es mas rapido y confiable que un agente LLM orquestando scrapers. Seria impresionante en presentacion pero riesgoso de implementar.

---

## Recomendacion Final: Que Usar

### Prioridad ALTA (implementar si o si)

| Caso de Uso | Modelo | Razon |
|-------------|--------|-------|
| OCR de screenshots (Plan B) | `qwen3-vl:8b` | Garantiza datos aunque scraping falle + demuestra AI |
| Generacion de insights | `qwen3.5:9b` | Core del 30% de evaluacion + diferenciador |

### Prioridad MEDIA (si hay tiempo)

| Caso de Uso | Modelo | Razon |
|-------------|--------|-------|
| Product matching | `nomic-embed-text` | Mejora calidad de normalizacion |
| Parseo fallback | `qwen3.5:4b` | Robustez cuando selectores fallan |

### NO usar (overengineering para este scope)

| Modelo | Razon de descarte |
|--------|-------------------|
| `gpt-oss:20b` | Muy lento, qwen3.5:9b es suficiente |
| `okamototk/gemma3-tools:12b` | Agente orquestador es overengineering |
| `translategemma:4b` | No se necesita traduccion |
| `deepseek-r1:3b` | Razonamiento puro sin ventaja practica aqui |
| `gemma3:270m`, `gemma3:1b` | Muy pequenos, calidad insuficiente |
| `qwen3.5:0.8b` | Muy pequeno para tareas utiles |
| `qwen3-embedding:4b` | nomic-embed-text es mejor para este caso |
| `embeddinggemma` | Mismo, nomic es mejor opcion |

---

## Flujo del Sistema con IA Local

```
SCRAPING (70%)
==============
Playwright/Nodriver → Extrae datos del DOM
                          |
                          +--[OK]--> JSON raw
                          |
                          +--[FALLO: selector roto]
                          |       |
                          |       v
                          |   qwen3.5:4b → Parsea texto crudo → JSON
                          |
                          +--[FALLO: anti-bot bloqueó]
                                  |
                                  v
                              Screenshot automatico
                                  |
                                  v
                              qwen3-vl:8b → OCR → JSON

NORMALIZACION
=============
nomic-embed-text → Matching de productos entre plataformas
                        |
                        v
                   CSV consolidado

INSIGHTS (30%)
==============
CSV consolidado → qwen3.5:9b → 5 Insights accionables
                                    |
                                    v
                               Informe final (HTML/PDF)
```

---

## Impacto en la Evaluacion

Usar modelos locales de Ollama agrega valor en:

1. **Diseno Tecnico (10%):** Demuestra arquitectura con IA integrada
2. **Calidad de Insights (15%):** Insights generados/asistidos por IA
3. **Presentacion (20%):** "Uso modelos de IA locales para X, Y, Z" = wow factor
4. **Calidad Scraping (50%):** Plan B con OCR = robustez

**El rol es AI Engineer. Usar IA local no es un extra, es lo que esperan ver.**
