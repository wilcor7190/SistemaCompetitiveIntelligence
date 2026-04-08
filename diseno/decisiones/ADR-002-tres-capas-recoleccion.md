# ADR-002: Sistema de 3 Capas de Recoleccion de Datos

**Estado:** Aceptado  
**Fecha:** 2026-04-07

## Contexto

El caso tecnico requiere construir un sistema de scraping que recolecte datos de 3 plataformas de delivery. El scraping clasico (browser automation + selectores CSS) es la tecnica estandar, pero tiene un problema fundamental: **es fragil**.

### La Realidad del Scraping en 2026

| Plataforma | Anti-bot detectado | Riesgo de bloqueo |
|------------|-------------------|-------------------|
| Uber Eats | Arkose, botdefense, reCAPTCHA | ALTO |
| Rappi | reCAPTCHA | MEDIO |
| DiDi Food | Desconocido, SPA pesada sin server-rendering | MEDIO-ALTO |

El brief del caso reconoce este riesgo:

> "Que pasa si me bloquean durante el scraping? Es parte del desafio."

Un scraper que solo tiene una forma de obtener datos **falla completamente** cuando esa forma deja de funcionar. Para un caso donde el scraping vale el 70% del entregable y 50% de la evaluacion, esto es un riesgo inaceptable.

### El Rol de AI Engineer

El puesto es AI Engineer, no Web Scraper. Usar unicamente scraping clasico no diferencia al candidato. Integrar IA en el flujo de recoleccion demuestra competencia en el rol.

## Decision

**Implementar un sistema de 3 capas de recoleccion con fallback automatico.**

```
CAPA 1: API Interception (preferida)
═════════════════════════════════════
Playwright intercepta network requests → descubre endpoints API internos
→ llama directo con aiohttp → JSON limpio

  Velocidad:  ★★★★★ (rapido, sin renderizar DOM)
  Estabilidad: ★★★★☆ (APIs internas son estables)
  Deteccion:  ★★★★★ (request HTTP normal, no bot behavior)
  Completitud: ★★★★☆ (puede tener datos que no estan en el DOM)

CAPA 2: DOM Parsing (clasica)
═════════════════════════════════════
Playwright navega como usuario → selectores CSS extraen datos del DOM
→ si selectores fallan, qwen3.5:4b parsea texto crudo

  Velocidad:  ★★★☆☆ (requiere renderizar JS)
  Estabilidad: ★★★☆☆ (selectores pueden cambiar)
  Deteccion:  ★★★☆☆ (browser automation detectable)
  Completitud: ★★★★★ (acceso a todo lo visible)

  Sub-fallback: qwen3.5:4b parsea texto desestructurado
    → Cuando selectores CSS se rompen pero la pagina cargo
    → El LLM local extrae datos del texto crudo de la pagina

CAPA 3: Screenshot + Vision AI (inteligente)
═════════════════════════════════════
Playwright captura screenshot → qwen3-vl:8b (Ollama) → OCR inteligente → JSON

  Velocidad:  ★★☆☆☆ (captura + inferencia ~3-5s)
  Estabilidad: ★★★★★ (si la pagina renderiza, siempre funciona)
  Deteccion:  ★★★★★ (screenshot es operacion local)
  Completitud: ★★★☆☆ (depende de lo visible en pantalla)

  Bonus: Las screenshots quedan como EVIDENCIA visual
    → El brief menciona "capturas automaticas de pantalla" como bonus
```

### Flujo de Fallback

```
Para cada (plataforma, direccion):
  1. Intentar Capa 1 (API interception)
     └─ Exito? → guardar datos, siguiente
     └─ Fallo? → intentar Capa 2

  2. Intentar Capa 2 (DOM parsing)
     └─ Exito? → guardar datos, siguiente
     └─ Selectores rotos? → qwen3.5:4b parsea texto
        └─ Exito? → guardar datos, siguiente
        └─ Fallo? → intentar Capa 3

  3. Intentar Capa 3 (Screenshot + OCR)
     └─ Exito? → guardar datos + screenshot como evidencia
     └─ Fallo? → ScrapedResult(success=False), loguear, continuar
```

## Alternativas Consideradas

### A. Solo scraping clasico (DOM parsing) - RECHAZADA
- **Pro:** Simple, bien documentado, rapido de implementar
- **Contra:** Un cambio en anti-bot o selectores = 0 datos
- **Contra:** No demuestra skills de AI Engineering
- **Contra:** Pregunta del evaluador "y si falla?" tiene mala respuesta

### B. Solo API interception - RECHAZADA
- **Pro:** Datos limpios, rapido
- **Contra:** No todas las plataformas exponen APIs utiles sin auth
- **Contra:** DiDi Food puede requerir tokens complejos

### C. Solo vision (screenshots + OCR) - RECHAZADA
- **Pro:** Siempre funciona si la pagina renderiza
- **Contra:** Lento (~3-5s por imagen × 375 data points = ~30 min)
- **Contra:** Precision de OCR puede fallar en decimales
- **Contra:** No aprovecha datos estructurados disponibles

### D. Sistema de 3 capas con fallback (ACEPTADA)
- **Pro:** Resiliencia maxima: no hay escenario sin datos
- **Pro:** Demuestra AI Engineering (vision + LLM local)
- **Pro:** Cada capa tiene fortalezas complementarias
- **Pro:** Screenshots como evidencia = bonus del brief
- **Contra:** Mas codigo, mas complejidad
- **Mitigacion:** La logica de fallback esta en BaseScraper, cada plataforma solo implementa sus metodos abstractos

## Consecuencias

### Positivas
- **Resiliencia**: No hay escenario donde el sistema no obtenga datos
- **Diferenciacion**: "Tengo 3 capas de recoleccion" vs "tengo un scraper"
- **Evidencia**: Screenshots automaticos = bonus de evaluacion
- **AI Integration**: Justifica el titulo de AI Engineer con uso real de modelos locales
- **Narrativa**: En la presentacion se puede mostrar el fallback en accion

### Negativas
- **Complejidad**: Mas codigo en BaseScraper para manejar las 3 capas
- **Mitigacion**: La logica de fallback es generica; cada scraper solo implementa selectores y URLs
- **Dependencia Ollama**: Capas 2 (fallback) y 3 requieren Ollama corriendo
- **Mitigacion**: Si Ollama no esta disponible, se salta al siguiente intento o se loguea error

### Modelos Ollama Requeridos

| Capa | Modelo | RAM | Cuando se usa |
|------|--------|-----|---------------|
| 2 (fallback) | qwen3.5:4b | ~3GB | Selectores CSS rotos, texto desestructurado |
| 3 | qwen3-vl:8b | ~6GB | Anti-bot bloquea, DOM no carga |

Nota: Nunca se ejecutan simultaneamente. RAM maxima requerida: ~6GB.
