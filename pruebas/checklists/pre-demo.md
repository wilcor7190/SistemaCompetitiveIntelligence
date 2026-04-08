# Checklist Pre-Demo — Dia de la Presentacion

**Fecha:** ____-__-__
**Hora demo:** __:__

---

## Setup tecnico (15 min antes)

- [ ] Computador conectado a corriente
- [ ] Conexion a internet estable verificada
- [ ] venv activado: `source venv/Scripts/activate`
- [ ] Browser abierto con `reports/insights.html` listo
- [ ] Terminal abierta en `desarrollo/`
- [ ] Comando listo en buffer: `python -m src.main --debug`

## Backup en caso de fallo

- [ ] `data/backup/` con datos pre-scrapeados verificados
- [ ] `python -m src.main --use-backup` probado y funciona
- [ ] Screenshots de runs anteriores en `data/screenshots/`
- [ ] Reporte HTML pre-generado abierto en otra pestania

## Material de presentacion

- [ ] Slides cargados (si aplica)
- [ ] Notas de presentacion impresas o en otra pantalla
- [ ] Cronometro listo (20 min de demo + 10 min Q&A)

## Demo flow (orden recomendado)

1. **Intro (2 min)**: que es el sistema, problema que resuelve
2. **Arquitectura (3 min)**: 3 capas, ADRs principales
3. **Demo en vivo (5 min)**: `python -m src.main --debug`
4. **Reporte HTML (5 min)**: abrir insights.html, recorrer secciones
5. **Insights (3 min)**: explicar 1-2 insights con datos reales
6. **Limitaciones (1 min)**: DiDi parcial, service fee, mejoras futuras
7. **Q&A (10 min)**: preguntas tecnicas

## Si algo falla durante demo

- **Scraping en vivo crashea** -> usar `--use-backup`
- **Browser bloqueado** -> mostrar reports/insights.html ya generado
- **Internet falla** -> usar datos de backup, mostrar arquitectura
- **Pregunta dificil** -> "Buena pregunta, esta documentado en `diseno/decisiones/`"

## Despues del demo

- [ ] Apuntar feedback recibido
- [ ] Cerrar terminales y guardar logs
- [ ] Commit final si hay correcciones de ultimo minuto
