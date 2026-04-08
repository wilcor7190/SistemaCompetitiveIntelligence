# ADR-001: Orden de Implementacion de Plataformas (Rappi Primero)

**Estado:** Aceptado  
**Fecha:** 2026-04-07

## Contexto

El caso tecnico requiere scrapear 3 plataformas de delivery: Rappi, Uber Eats y DiDi Food. La arquitectura inicial (doc 05) proponia empezar por Uber Eats por ser la plataforma mas documentada y con mejor soporte de Playwright. Sin embargo, el spike tecnico de reconocimiento (doc 09) revelo informacion que cambia esta prioridad.

### Hallazgos del Spike Tecnico

| Plataforma | Precios sin login | Anti-bot | Tecnologia Web | Accesibilidad |
|------------|-------------------|----------|----------------|---------------|
| **Rappi** | SI | reCAPTCHA (medio) | Next.js + PWA | ALTA |
| **Uber Eats** | SI | Arkose + botdefense (alto) | React + Next.js SPA | MEDIA-ALTA |
| **DiDi Food** | No verificado | Desconocido | SPA vanilla + JS pesado | BAJA |

### Factores Adicionales

- **Rappi es el baseline del caso**: El brief dice "competitive intelligence para Rappi". Tener datos propios de Rappi primero da contexto inmediato para comparar.
- **Rappi muestra mas datos sin interaccion**: Tiempo de entrega (35 min) y promociones visibles sin configurar direccion.
- **Rappi tiene selectores CSS mas estables**: PWA con estructura predecible vs Uber Eats con Styled Components y hashes.
- **Rappi tiene URLs predecibles**: `/restaurantes/{id}-{nombre}` con IDs numericos vs hashes de Uber.

## Decision

**Cambiar el orden de implementacion a: Rappi → Uber Eats → DiDi Food.**

```
ORDEN ORIGINAL (propuesto en doc 05):
  1. Uber Eats  → API interception
  2. Rappi      → Playwright
  3. DiDi Food  → Playwright

ORDEN NUEVO (basado en spike doc 09):
  1. Rappi      → Primero: mas accesible, baseline propio, menos anti-bot
  2. Uber Eats  → Segundo: bien documentado pero anti-bot mas agresivo
  3. DiDi Food  → Tercero: el mas dificil, con Plan B (OCR) si es necesario
```

## Alternativas Consideradas

### A. Mantener Uber Eats primero (RECHAZADA)
- **Pro:** Mas documentacion disponible sobre scraping de Uber Eats
- **Contra:** Anti-bot (Arkose/botdefense) es mas agresivo, riesgo de perder tiempo en la primera plataforma
- **Contra:** No es el baseline del caso

### B. Empezar por DiDi Food (RECHAZADA)
- **Pro:** Atacar lo mas dificil primero
- **Contra:** SPA pesada, posible login requerido, no se pudieron verificar precios en el spike
- **Contra:** Si falla, perdemos tiempo critico sin datos de ninguna plataforma

### C. Empezar por Rappi (ACEPTADA)
- **Pro:** Datos accesibles verificados en el spike (Big Mac Tocino $155, McNuggets $145, Papas $75)
- **Pro:** Es el baseline del caso (Rappi quiere compararse con la competencia)
- **Pro:** Menor riesgo de anti-bot = datos garantizados rapido
- **Pro:** URLs descubiertas: `rappi.com.mx/restaurantes/1306705702-mcdonalds`
- **Contra:** Selectores CSS pueden ser dinamicos (Styled Components)

## Consecuencias

### Positivas
- **Datos rapido**: Al terminar MVP 0, ya tenemos datos reales de la plataforma mas accesible
- **Baseline primero**: Podemos comparar Uber Eats y DiDi contra Rappi (la perspectiva correcta del caso)
- **Menor riesgo**: Si Rappi funciona bien, la confianza y el codigo base facilitan las siguientes plataformas
- **Insights tempranos**: Ya en el spike encontramos diferencias reales (McNuggets: $145 Rappi vs $155 Uber = -6.5%)

### Negativas
- **Styled Components**: Los selectores CSS de Rappi pueden tener hashes que cambian entre deployments
- **Mitigacion**: API interception (Capa 1) como primera opcion, y vision fallback (Capa 3) como backup

### Impacto en el Roadmap

| MVP | Antes | Ahora |
|-----|-------|-------|
| MVP 0 (PoC) | `feature/poc-uber-eats` | `feature/poc-rappi` |
| MVP 1 (Single platform) | `feature/uber-eats-scraper` | `feature/rappi-scraper` |
| MVP 2 (Multi-platform) | Sin cambio | Sin cambio (se agregan las 3) |
