---
name: diseno
description: >
  Fase de diseno tecnico y arquitectura del sistema.
  Trigger: Cuando se crean diagramas de arquitectura, se disenan clases,
  se definen schemas de datos, o se toman decisiones tecnicas.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Creating architecture diagrams or technical design"
    - "Designing data schemas or class hierarchies"
    - "Making technology decisions"
    - "Working on files in diseno/"
    - "Creating ADRs or architecture decisions"
allowed-tools: Read, Edit, Write, Glob, Grep
---

## When to Use

1. Designing system architecture or component interactions
2. Creating or modifying data models/schemas
3. Making technology selection decisions

## Critical Patterns

### Architecture Decisions
Every design decision must document:
- **Context**: What problem are we solving?
- **Decision**: What did we choose?
- **Rationale**: Why this option over alternatives?
- **Consequences**: What trade-offs does this create?

### Data Model Design
All models use Pydantic dataclasses in `desarrollo/src/models/schemas.py`:
- Use type hints strictly
- Include `| None` for optional fields
- Add validation where needed

### Diagram Format
Use Mermaid for all diagrams:
- `graph TB` for architecture
- `sequenceDiagram` for flows
- `pie` for distributions

## Decision Tree

- Designing a new component?
  → Check `Analisis/05-arquitectura-propuesta.md` first
- Choosing a technology?
  → Check `Analisis/06-decision-matrix.md` first
- Adding a new data field?
  → Update `desarrollo/src/models/schemas.py` and document in architecture doc

## Working Directory

All design artifacts go in `diseno/` (NOT in `Analisis/` which is for requirements analysis).

- `diseno/AGENTS.md` → Local agent guidelines for this folder
- `diseno/arquitectura/` → Architecture diagrams
- `diseno/modelos/` → Data model schemas
- `diseno/decisiones/` → ADRs (Architecture Decision Records)
- `diseno/dashboard/` → Dashboard wireframes

See [diseno/AGENTS.md](../../diseno/AGENTS.md) for full structure and naming conventions.

## Key Architecture References

- **Scraper pattern**: BaseScraper abstract class in `desarrollo/src/scrapers/base.py`
- **Data flow**: Scraper → Normalizer → Merger → Reporter
- **Config**: JSON for addresses/products, YAML for settings
- **Output**: JSON (raw) + CSV (merged)
