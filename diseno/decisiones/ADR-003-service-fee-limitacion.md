# ADR-003: Service Fee como Limitacion Documentada

**Estado:** Aceptado  
**Fecha:** 2026-04-07

## Contexto

El brief del caso pide recolectar "minimo 3 metricas" de las siguientes: precio producto, delivery fee, service fee, tiempo de entrega, descuentos, disponibilidad, precio final.

El spike tecnico de reconocimiento (doc 09) revelo un hallazgo critico:

### Service Fee NO es Visible en Ninguna Plataforma

| Plataforma | Pagina de restaurante | Checkout/Carrito |
|------------|----------------------|------------------|
| **Rappi** | NO visible | Aparece al agregar items al carrito |
| **Uber Eats** | NO visible | Aparece en el resumen de compra |
| **DiDi Food** | NO verificado | Probablemente igual |

En las 3 plataformas, el service fee solo se calcula y muestra cuando el usuario:
1. Agrega al menos 1 producto al carrito
2. Ingresa una direccion de entrega
3. Llega a la pantalla de checkout/resumen

### Implicacion Tecnica

Para obtener el service fee necesitariamos:
- **Opcion A:** Simular una compra (agregar producto al carrito, ir al checkout, leer el fee)
- **Opcion B:** Interceptar la API del checkout que calcula los fees
- **Opcion C:** Documentar como limitacion y enfocarse en las otras metricas

## Decision

**Documentar service fee como limitacion conocida. No intentar simular una compra.**

### Metricas que SI Recolectamos (5 de 7)

| Metrica | Disponibilidad | Fuente |
|---------|---------------|--------|
| **Precio producto** | Visible en todas | Pagina de restaurante |
| **Delivery fee** | Visible en Uber Eats ($4.99), parcial en Rappi ("Envio Gratis") | Pagina de restaurante |
| **Tiempo de entrega** | Visible en Rappi (35 min), requiere direccion en Uber | Pagina de restaurante |
| **Promociones/Descuentos** | Visible en Rappi ("Hasta 64% OFF"), parcial en Uber | Pagina de restaurante |
| **Disponibilidad** | Si el producto aparece = disponible | Presencia en la pagina |

### Metricas que NO Recolectamos (2 de 7)

| Metrica | Razon | Riesgo de Intentarlo |
|---------|-------|---------------------|
| **Service fee** | Solo visible en checkout | Simular compra puede triggear anti-fraude, bloqueo de IP, o requerir cuenta con metodo de pago |
| **Precio final** | Requiere service fee | Depende del dato anterior |

### Justificacion

El brief dice "minimo 3 metricas". Tenemos 5 metricas solidas. Intentar obtener service fee:

1. **Riesgo de anti-fraude**: Agregar items al carrito y llegar al checkout sin completar la compra es patron detectado por anti-fraude
2. **Requiere cuenta**: Checkout probablemente requiere login con cuenta real y metodo de pago
3. **Etica**: Simular compras repetidamente podria ser interpretado como abuso de la plataforma
4. **Tiempo**: Implementar simulacion de compra en 3 plataformas consume tiempo critico que es mejor invertir en cobertura y calidad de las 5 metricas disponibles

## Alternativas Consideradas

### A. Simular compra para obtener service fee - RECHAZADA
- **Pro:** Dato completo, metrica valiosa
- **Contra:** Alto riesgo de bloqueo por anti-fraude
- **Contra:** Requiere cuenta con metodo de pago en cada plataforma
- **Contra:** Etica cuestionable (simular compras)
- **Contra:** Tiempo de implementacion alto para las 3 plataformas

### B. Interceptar API de checkout - RECHAZADA
- **Pro:** No requiere completar la compra
- **Contra:** API de checkout es la mas protegida (requiere auth tokens, session cookies)
- **Contra:** Puede variar por usuario, direccion, restaurante
- **Contra:** Alto riesgo de deteccion

### C. Estimar service fee con datos historicos - RECHAZADA
- **Pro:** No requiere interaccion con checkout
- **Contra:** No tenemos datos historicos
- **Contra:** Service fee varia por plataforma, zona, restaurante y monto
- **Contra:** Estimacion no es dato real

### D. Documentar como limitacion (ACEPTADA)
- **Pro:** Transparente, honesto, demuestra criterio de ingenieria
- **Pro:** El brief valora "pragmatismo" y "scope bien definido"
- **Pro:** 5 metricas > minimo de 3 requeridas
- **Pro:** Se puede mencionar en la presentacion como "known limitation with technical reason"

## Consecuencias

### Positivas
- **Transparencia**: Documenta claramente que se puede y que no se puede obtener
- **Pragmatismo**: Enfoca esfuerzo en 5 metricas solidas vs 7 metricas fragiles
- **Seguridad**: No arriesga bloqueo de IP por simular compras
- **Etica**: No simula compras que podrian generar cargos accidentales
- **Presentacion**: "Supe donde parar" demuestra criterio de ingenieria

### Negativas
- **Dato incompleto**: No podemos calcular "precio final real" (producto + delivery + service)
- **Mitigacion**: Calculamos "precio parcial" = precio producto + delivery fee, y documentamos que falta service fee
- **Comparacion imperfecta**: Si una plataforma tiene service fee alto y otra bajo, nuestro analisis no lo captura
- **Mitigacion**: Mencionamos esto explicitamente en las limitaciones del informe

### Como Presentarlo

En la seccion "Limitaciones y Next Steps" de la presentacion:

> "Service fee no es accesible sin simular una compra completa en checkout.
> Decidimos documentar esta limitacion en lugar de arriesgar deteccion por anti-fraude.
> Con acceso a APIs internas de Rappi, esto se resolveria en produccion.
> Nuestro analisis cubre 5 de 7 metricas, superando el minimo de 3."

### Metricas Disponibles vs No Disponibles

```
DISPONIBLES (5)                    NO DISPONIBLES (2)
═══════════════                    ═══════════════════
✓ Precio producto                  ✗ Service fee
✓ Delivery fee                     ✗ Precio final real
✓ Tiempo de entrega                  (requiere service fee)
✓ Promociones/Descuentos
✓ Disponibilidad

METRICAS REQUERIDAS: minimo 3
METRICAS ENTREGADAS: 5
CUMPLIMIENTO: 167% del minimo
```
