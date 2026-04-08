---
name: analisis
description: >
  Fase de analisis de requerimientos y contexto de negocio.
  Trigger: Cuando se analizan requerimientos, se investiga el mercado,
  se documenta contexto de negocio, o se trabaja en Analisis/*.md
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Analyzing requirements or business context"
    - "Investigating market alternatives"
    - "Working on Analisis/ documents"
allowed-tools: Read, Edit, Write, Glob, Grep, WebFetch, WebSearch
---

## When to Use

1. User asks to analyze, investigate, or research any aspect of the project
2. Working on any file inside `Analisis/` directory
3. Discussing business context, competitors, or market dynamics

## Critical Patterns

### Document Naming Convention
Files in `Analisis/` follow: `NN-nombre-descriptivo.md` (e.g., `01-resumen-requerimiento.md`)

### Analysis Structure
Every analysis document must include:
- Clear section headers
- Data-backed claims (reference sources)
- Comparison tables where applicable
- Diagrams (mermaid) for complex concepts
- Actionable conclusions

## Decision Tree

- Is this a new analysis topic?
  → Create new `Analisis/NN-topic.md` with next sequential number
- Is this updating existing analysis?
  → Edit the existing file, preserve structure
- Does it need market research?
  → Use WebSearch first, document sources
- Does it need competitive data?
  → Reference existing analysis docs in `Analisis/02-analisis-mercado.md`

## Existing Analysis Documents

| File | Content |
|------|---------|
| `01-resumen-requerimiento.md` | Case requirements synthesis |
| `02-analisis-mercado.md` | Market tools & alternatives |
| `03-enfoques-solucion.md` | 5 solution approaches compared |
| `04-mvp-roadmap.md` | Incremental MVP plan |
| `05-arquitectura-propuesta.md` | Architecture & class design |
| `06-decision-matrix.md` | Technology decision scoring |

## Commands

```bash
# List all analysis documents
ls -la Analisis/*.md

# Count lines per document
wc -l Analisis/*.md
```
