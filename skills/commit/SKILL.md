---
name: commit
description: >
  Conventional commits con versionamiento semantico.
  Trigger: Cuando se crea un git commit, se etiqueta una version,
  o se necesita decidir el tipo de commit.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Creating a git commit"
    - "Committing changes"
    - "Tagging a release version"
allowed-tools: Read, Edit, Write, Bash
---

## When to Use

1. About to create a git commit
2. Deciding commit type or scope
3. Tagging a version release

## Critical Patterns

### Commit Format (Non-negotiable)
```
<type>(scope): <description>

[optional body]

[optional footer]
```

- First line MUST be under 72 characters
- Description in imperative mood: "add" not "added" or "adds"
- No period at the end of the description

### Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `chore` | Maintenance, dependencies, config |
| `refactor` | Code change that neither fixes nor adds |
| `test` | Adding or updating tests |
| `perf` | Performance improvement |
| `style` | Formatting, no code change |

### Scopes

| Scope | When |
|-------|------|
| `scraper` | Changes in src/scrapers/ |
| `analysis` | Changes in src/analysis/ |
| `processor` | Changes in src/processors/ |
| `model` | Changes in src/models/ |
| `config` | Changes in config/ |
| `data` | Changes in data/ |
| `docs` | Changes in Analisis/ or README |
| `ci` | Changes in CI/CD |
| `skills` | Changes in skills/ |
| _(omit)_ | Multiple areas or root files |

### Workflow (Non-negotiable)

```
1. git status → See what changed
2. git diff → Understand the changes
3. Draft commit message → Present to user
4. WAIT for user approval → Never commit without asking
5. git add <specific files> → Stage only relevant files
6. git commit -m "..." → Create the commit
```

### Rules

- **NEVER** commit without user approval
- **NEVER** use `git add .` or `git add -A` (stage specific files)
- **NEVER** use `--force` or `-f` on push
- **NEVER** commit .env, API keys, or credentials
- **NEVER** amend a commit unless explicitly asked
- **ALWAYS** use specific file names in `git add`

### Examples

```bash
# Feature: new scraper
feat(scraper): add Uber Eats price extraction for CDMX

# Fix: handle edge case
fix(scraper): handle missing delivery fee in DiDi Food response

# Docs: analysis
docs: add market analysis and solution approaches

# Chore: config
chore(config): add 15 new addresses for Polanco zone

# Test
test(model): add validation tests for ScrapedResult schema

# Refactor
refactor(processor): simplify CSV merge logic
```

### Version Tagging

```bash
# After merging to main, tag with semantic version
git tag -a v0.1.0 -m "MVP 0+1: Single platform scraper"
git tag -a v0.2.0 -m "MVP 2: Multi-platform scraping"
git tag -a v0.3.0 -m "MVP 3: Insights and visualizations"
git tag -a v0.4.0 -m "MVP 4: Polish and presentation"
```
