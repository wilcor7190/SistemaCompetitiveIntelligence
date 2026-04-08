---
name: pr
description: >
  Convenciones de Pull Request para el proyecto.
  Trigger: Cuando se crea un PR, se revisa un PR,
  o se prepara codigo para merge.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Creating a Pull Request"
    - "Reviewing a Pull Request"
    - "Preparing code for merge"
allowed-tools: Read, Edit, Write, Bash, Grep
---

## When to Use

1. Creating a Pull Request with `gh pr create`
2. Reviewing or updating an existing PR
3. Merging branches

## Critical Patterns

### PR Title
Follow conventional commit format: `<type>(scope): <description>`

### PR Body Template (Non-negotiable)

```markdown
## Summary
- [1-3 bullet points explaining WHAT and WHY]

## Changes
- [ ] List of specific changes made

## Testing
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Lint passes: `ruff check src/`
- [ ] Manual verification: [describe what you checked]

## Screenshots
[If UI/visual changes, include before/after]

## Related
- Closes #XX (if applicable)
- Related to MVP N

## Checklist
- [ ] Code follows project conventions
- [ ] No credentials or .env committed
- [ ] Documentation updated if needed
```

### PR Workflow

```
1. Ensure branch is up to date with target
2. Run tests and lint
3. Review diff: git diff develop...HEAD
4. Create PR: gh pr create --title "..." --body "..."
5. Request review if applicable
```

### Merge Strategy

| From | To | Method |
|------|----|--------|
| `feature/*` | `develop` | Squash merge |
| `fix/*` | `develop` | Squash merge |
| `release/*` | `main` | Merge commit |
| `hotfix/*` | `main` | Merge commit |
| `develop` | `main` | Merge commit (via release branch) |

## Commands

```bash
# Create PR
gh pr create --title "feat(scraper): add Uber Eats scraper" --body "..."

# List open PRs
gh pr list

# View PR status
gh pr view

# Merge PR (squash)
gh pr merge --squash
```
