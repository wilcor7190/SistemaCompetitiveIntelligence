---
name: gitflow
description: >
  Branching strategy, versionamiento semantico y GitFlow.
  Trigger: Cuando se crean/mergean branches, se tagean versiones,
  se hace release, o se necesita revertir a version anterior.
license: MIT
metadata:
  author: wilcor7190
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Creating/merging branches or releasing versions"
    - "Tagging a release version"
    - "Reverting to a previous version"
    - "Setting up git repository"
allowed-tools: Read, Edit, Write, Bash
---

## When to Use

1. Creating a new branch for a feature/fix
2. Merging branches or preparing a release
3. Tagging a version
4. Reverting to a previous stable version

## Critical Patterns

### Branch Structure

```
main                    ← Tagged releases only (v0.1.0, v0.2.0...)
│                         Always deployable/presentable
│
├── develop             ← Integration branch
│   │                     Latest working code, all features merged here
│   │
│   ├── feature/*       ← New features
│   │   Examples:
│   │   feature/poc-uber-eats
│   │   feature/uber-eats-scraper
│   │   feature/multi-platform
│   │   feature/insights-report
│   │   feature/dashboard
│   │
│   ├── fix/*           ← Bug fixes
│   │   Examples:
│   │   fix/proxy-rotation
│   │   fix/missing-delivery-fee
│   │
│   └── docs/*          ← Documentation
│       Examples:
│       docs/analisis
│       docs/readme-update
│
├── release/*           ← Release candidates
│   Examples:
│   release/v0.1.0
│   release/v0.4.0
│
└── hotfix/*            ← Emergency fixes on main
    Examples:
    hotfix/critical-scraper-bug
```

### Branch Naming (Non-negotiable)

```
<type>/<short-description>

Types: feature, fix, docs, release, hotfix
Description: kebab-case, max 5 words
```

### Version Strategy (Semantic Versioning)

```
v{MAJOR}.{MINOR}.{PATCH}

MAJOR = Breaking changes (v1.0.0 = final deliverable)
MINOR = New features/MVPs (v0.1.0, v0.2.0...)
PATCH = Bug fixes (v0.1.1)
```

### MVP to Version Mapping

| MVP | Version | Branch | What's included |
|-----|---------|--------|-----------------|
| MVP 0 | v0.1.0-alpha | feature/poc-uber-eats | PoC 1 platform, 1 address |
| MVP 1 | v0.1.0 | feature/uber-eats-scraper | UberEats multi-address |
| MVP 2 | v0.2.0 | feature/multi-platform | 3 platforms integrated |
| MVP 3 | v0.3.0 | feature/insights-report | Analysis + visualizations |
| MVP 4 | v0.4.0 | release/v0.4.0 | Polish + presentation |
| MVP 5 | v0.5.0 | feature/dashboard | Streamlit (bonus) |
| Final | v1.0.0 | main | Complete deliverable |

### Workflow

```
1. Create feature branch from develop
   git checkout develop
   git checkout -b feature/uber-eats-scraper

2. Work on feature, commit regularly
   git add src/scrapers/uber_eats.py
   git commit -m "feat(scraper): add UberEats price extraction"

3. When feature is complete, merge to develop
   git checkout develop
   git merge --no-ff feature/uber-eats-scraper

4. When MVP milestone reached, create release
   git checkout -b release/v0.1.0
   # Final testing, version bump
   git checkout main
   git merge --no-ff release/v0.1.0
   git tag -a v0.1.0 -m "MVP 1: Single platform scraper"

5. Push tags
   git push origin main --tags
```

### Reverting to a Previous Version

```bash
# See all tagged versions
git tag -l

# Checkout a specific version (detached HEAD)
git checkout v0.2.0

# Create branch from old version (to fix something)
git checkout -b hotfix/from-v0.2.0 v0.2.0

# Reset develop to a known good version (DESTRUCTIVE - ask user first)
# git reset --hard v0.2.0
```

## Remote Repository

```bash
# Initial setup
git remote add origin https://github.com/wilcor7190/SistemaCompetitiveIntelligence.git

# Push with tags
git push -u origin main
git push -u origin develop
git push origin --tags

# Push feature branch
git push -u origin feature/uber-eats-scraper
```

## Rules

- **NEVER** push directly to `main` (always through release/ or hotfix/)
- **NEVER** force push to `main` or `develop`
- **ALWAYS** tag releases on `main` with semantic version
- **ALWAYS** merge with `--no-ff` to preserve branch history
- **ALWAYS** delete feature branches after merge (keep them clean)

## Commands

```bash
# Setup initial branches
git init
git checkout -b main
git checkout -b develop

# See branch graph
git log --oneline --graph --all

# List tags
git tag -l -n1

# Compare two versions
git diff v0.1.0..v0.2.0 --stat
```
