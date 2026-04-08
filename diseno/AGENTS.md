# Fase: Diseno Tecnico

> Este archivo guia al agente cuando trabaja dentro de `diseno/`.
> Overrides sobre el AGENTS.md raiz para esta fase.

## Proposito de esta carpeta

Contiene todos los artefactos de diseno tecnico y arquitectura del sistema:
- Diagramas de arquitectura (Mermaid)
- Diseno de clases y modelos de datos
- Decisiones tecnicas documentadas (ADRs)
- Wireframes o mockups de dashboards
- Schemas de datos (JSON Schema, Pydantic)

## Estructura

```
diseno/
├── AGENTS.md                    # THIS FILE
├── arquitectura/                # Diagramas de arquitectura
│   ├── sistema-general.md       # Diagrama general del sistema
│   ├── flujo-datos.md           # Flujo de datos scraper -> report
│   └── componentes.md           # Diagrama de componentes
├── modelos/                     # Diseno de modelos de datos
│   ├── schemas.md               # Definicion de schemas Pydantic
│   └── normalizacion.md         # Reglas de normalizacion entre plataformas
├── decisiones/                  # Architecture Decision Records
│   └── ADR-NNN-titulo.md        # Formato: ADR-001-eleccion-playwright.md
└── dashboard/                   # Diseno de dashboard (si aplica)
    └── wireframes.md
```

## Convenciones

### Nombres de archivos
- Kebab-case: `flujo-datos.md`, `schema-scraping.md`
- ADRs numerados: `ADR-001-titulo.md`

### Formato de ADR (Architecture Decision Record)
```markdown
# ADR-NNN: Titulo de la Decision

**Estado:** Aceptado | Propuesto | Deprecado
**Fecha:** YYYY-MM-DD

## Contexto
[Que problema estamos resolviendo]

## Decision
[Que decidimos hacer]

## Alternativas Consideradas
[Que otras opciones evaluamos]

## Consecuencias
[Que trade-offs acepta esta decision]
```

### Diagramas
- Usar Mermaid exclusivamente (renderiza en GitHub)
- `graph TB` para arquitectura
- `sequenceDiagram` para flujos
- `classDiagram` para modelos
- `erDiagram` para relaciones de datos

## Skill asociado
Invoke `diseno` skill cuando trabajes en esta carpeta.

## Relacion con otras carpetas
- **Analisis/** → Input: los documentos de analisis alimentan el diseno
- **desarrollo/** → Output: el diseno guia la implementacion
- **src/** → Los schemas aqui se implementan en `src/models/`
