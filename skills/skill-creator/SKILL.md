---
name: skill-creator
description: >
  Crea nuevas AI agent skills siguiendo la estructura del proyecto.
  Trigger: Cuando el usuario pide crear una nueva skill, agregar
  instrucciones para el agente, o documentar patrones recurrentes.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Creating new skills"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

## When to Create a Skill

Create a skill when:
- A pattern repeats across multiple tasks
- Project conventions differ from defaults
- Workflows need step-by-step instructions
- Decision trees help choose approaches

Skip skill creation when:
- Documentation already exists elsewhere
- Patterns are trivial or obvious
- Tasks are one-time only

## Critical Patterns

### Skill Directory Structure

```
skills/{skill-name}/
├── SKILL.md              # Required: skill definition
├── assets/               # Optional: templates, schemas, scripts
│   ├── template.py
│   └── schema.json
└── references/           # Optional: local docs
    └── docs.md
```

### Naming Convention

- Generic skills: `{technology}` (e.g., `playwright`, `pytest`)
- Project-specific: `{action}` (e.g., `scraping`, `insights`)
- Workflow skills: `{process}` (e.g., `commit`, `gitflow`)

### SKILL.md Template

```yaml
---
name: {skill-name}
description: >
  {What this skill does}.
  Trigger: {When to activate this skill}.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "{Action 1 that triggers this}"
    - "{Action 2 that triggers this}"
allowed-tools: {comma-separated tools}
---

## When to Use
{3 numbered conditions}

## Critical Patterns
{Non-negotiable rules with code examples}

## Decision Tree
{Conditional logic: situation → action}

## Commands
{Relevant bash commands}
```

## After Creating a Skill

1. Add the skill to AGENTS.md "Project Skills" table
2. Add auto_invoke entries to AGENTS.md "Auto-invoke Skills" table
3. Run `bash skills/setup.sh --all` to sync and validate

## Commands

```bash
# Create skill directory
mkdir -p skills/{skill-name}

# Check for duplicate skill names
ls skills/

# Validate after creation
bash skills/setup.sh --validate
```
