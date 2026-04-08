---
name: skill-sync
description: >
  Sincroniza AGENTS.md a CLAUDE.md y valida skills.
  Trigger: Despues de crear/modificar una skill, o cuando se necesita
  regenerar CLAUDE.md desde AGENTS.md.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "After creating/modifying a skill"
    - "Regenerate AGENTS.md Auto-invoke tables"
    - "Troubleshoot why CLAUDE.md is out of sync"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

## When to Use

1. After creating or modifying any skill in `skills/`
2. When CLAUDE.md needs to be regenerated
3. When validating skill metadata

## Critical Patterns

### How AGENTS.md and CLAUDE.md Relate

```
AGENTS.md (source of truth)
    |
    | bash skills/setup.sh --sync
    |
    v
CLAUDE.md (auto-generated for Claude Code)
```

- **AGENTS.md**: Edit this file directly. Contains all project guidelines.
- **CLAUDE.md**: AUTO-GENERATED. Never edit directly. Claude Code reads this file.
- **setup.sh**: Copies AGENTS.md -> CLAUDE.md with sync metadata header.

### SKILL.md Required Frontmatter

```yaml
---
name: skill-name           # Required: lowercase, hyphens
description: >             # Required: what + trigger
  Description of the skill.
  Trigger: When X happens.
license: MIT               # Required
metadata:
  author: wilcor7190       # Required
  version: "1.0"           # Required
  scope: [root]            # Required: where this applies
  auto_invoke:             # Required for Auto-invoke table
    - "Action that triggers this skill"
allowed-tools: Read, Edit, Write  # Required: tools the agent can use
---
```

### Adding a New Skill to AGENTS.md

When a new skill is created:
1. Add it to the "Project Skills" table in AGENTS.md
2. Add its auto_invoke actions to the "Auto-invoke Skills" table
3. Run `bash skills/setup.sh --all` to sync and validate

## Commands

```bash
# Sync AGENTS.md -> CLAUDE.md
bash skills/setup.sh --sync

# Validate all skills
bash skills/setup.sh --validate

# Both
bash skills/setup.sh --all

# Show skill inventory
bash skills/setup.sh  # then select option 4
```
