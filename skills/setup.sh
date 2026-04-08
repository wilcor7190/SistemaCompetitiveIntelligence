#!/usr/bin/env bash
# =============================================================================
# Rappi CI - Skills Setup Script
# =============================================================================
# Syncs AGENTS.md -> CLAUDE.md for Claude Code compatibility.
# Also validates skill structure and generates auto-invoke tables.
#
# Usage:
#   bash skills/setup.sh              # Interactive mode
#   bash skills/setup.sh --sync       # Sync AGENTS.md to CLAUDE.md
#   bash skills/setup.sh --validate   # Validate all skills
#   bash skills/setup.sh --all        # Sync + Validate
#   bash skills/setup.sh --help       # Show help
# =============================================================================

set -euo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$PROJECT_ROOT/skills"
AGENTS_FILE="$PROJECT_ROOT/AGENTS.md"
CLAUDE_FILE="$PROJECT_ROOT/CLAUDE.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Flags
DO_SYNC=false
DO_VALIDATE=false

# --- Functions ---

show_help() {
    echo -e "${CYAN}Rappi CI - Skills Setup${NC}"
    echo ""
    echo "Usage: bash skills/setup.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --sync       Sync AGENTS.md content to CLAUDE.md"
    echo "  --validate   Validate all skill SKILL.md files"
    echo "  --all        Run sync + validate"
    echo "  --help       Show this help"
    echo ""
    echo "What this does:"
    echo "  1. Copies AGENTS.md -> CLAUDE.md (Claude Code reads CLAUDE.md)"
    echo "  2. Validates each skills/*/SKILL.md has required frontmatter"
    echo "  3. Reports skills without proper metadata"
    echo ""
}

show_menu() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  Rappi CI - Skills Setup${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC} Sync AGENTS.md -> CLAUDE.md"
    echo -e "  ${GREEN}2)${NC} Validate all skills"
    echo -e "  ${GREEN}3)${NC} Both (sync + validate)"
    echo -e "  ${GREEN}4)${NC} Show skill inventory"
    echo -e "  ${GREEN}5)${NC} Exit"
    echo ""
    read -rp "Select option [1-5]: " choice
    case "$choice" in
        1) DO_SYNC=true ;;
        2) DO_VALIDATE=true ;;
        3) DO_SYNC=true; DO_VALIDATE=true ;;
        4) show_inventory; exit 0 ;;
        5) exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}"; exit 1 ;;
    esac
}

sync_agents_to_claude() {
    echo -e "${BLUE}[SYNC]${NC} Syncing AGENTS.md -> CLAUDE.md..."

    if [[ ! -f "$AGENTS_FILE" ]]; then
        echo -e "${RED}[ERROR]${NC} AGENTS.md not found at $AGENTS_FILE"
        return 1
    fi

    # Copy AGENTS.md to CLAUDE.md with header comment
    {
        echo "<!-- AUTO-GENERATED: Do not edit directly. Edit AGENTS.md and run: bash skills/setup.sh --sync -->"
        echo "<!-- Last synced: $(date -u '+%Y-%m-%dT%H:%M:%SZ') -->"
        echo ""
        cat "$AGENTS_FILE"
    } > "$CLAUDE_FILE"

    echo -e "${GREEN}[OK]${NC} CLAUDE.md updated successfully"
    echo -e "     Source: AGENTS.md ($(wc -l < "$AGENTS_FILE") lines)"
    echo -e "     Target: CLAUDE.md ($(wc -l < "$CLAUDE_FILE") lines)"
}

validate_skills() {
    echo -e "${BLUE}[VALIDATE]${NC} Checking all skills..."
    echo ""

    local total=0
    local valid=0
    local invalid=0
    local missing_fields=()

    for skill_dir in "$SKILLS_DIR"/*/; do
        # Skip if not a directory or is assets
        [[ ! -d "$skill_dir" ]] && continue

        local skill_name
        skill_name=$(basename "$skill_dir")
        local skill_file="$skill_dir/SKILL.md"

        total=$((total + 1))

        if [[ ! -f "$skill_file" ]]; then
            echo -e "  ${RED}[MISSING]${NC} $skill_name/SKILL.md"
            invalid=$((invalid + 1))
            continue
        fi

        # Check required frontmatter fields
        local has_name=false
        local has_description=false
        local has_auto_invoke=false

        if grep -q "^name:" "$skill_file" 2>/dev/null; then has_name=true; fi
        if grep -q "^description:" "$skill_file" 2>/dev/null; then has_description=true; fi
        if grep -q "auto_invoke:" "$skill_file" 2>/dev/null; then has_auto_invoke=true; fi

        if $has_name && $has_description; then
            echo -e "  ${GREEN}[OK]${NC} $skill_name"
            valid=$((valid + 1))

            if ! $has_auto_invoke; then
                missing_fields+=("$skill_name (missing auto_invoke)")
            fi
        else
            echo -e "  ${YELLOW}[WARN]${NC} $skill_name - missing: $(! $has_name && echo 'name ')$(! $has_description && echo 'description ')"
            invalid=$((invalid + 1))
        fi
    done

    echo ""
    echo -e "${BLUE}[SUMMARY]${NC} $total skills found: ${GREEN}$valid valid${NC}, ${RED}$invalid invalid${NC}"

    if [[ ${#missing_fields[@]} -gt 0 ]]; then
        echo ""
        echo -e "${YELLOW}[INFO]${NC} Skills without auto_invoke (won't appear in Auto-invoke table):"
        for field in "${missing_fields[@]}"; do
            echo -e "  - $field"
        done
    fi
}

show_inventory() {
    echo -e "${CYAN}Skill Inventory${NC}"
    echo ""
    printf "%-20s %-50s %s\n" "SKILL" "DESCRIPTION" "FILES"
    printf "%-20s %-50s %s\n" "-----" "-----------" "-----"

    for skill_dir in "$SKILLS_DIR"/*/; do
        [[ ! -d "$skill_dir" ]] && continue

        local skill_name
        skill_name=$(basename "$skill_dir")
        local skill_file="$skill_dir/SKILL.md"

        local description="(no SKILL.md)"
        if [[ -f "$skill_file" ]]; then
            description=$(grep "^description:" "$skill_file" 2>/dev/null | head -1 | sed 's/^description: *//' | cut -c1-48)
        fi

        local file_count
        file_count=$(find "$skill_dir" -type f | wc -l | tr -d ' ')

        printf "%-20s %-50s %s\n" "$skill_name" "$description" "$file_count files"
    done
}

# --- Parse Arguments ---
if [[ $# -eq 0 ]]; then
    show_menu
else
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --sync)     DO_SYNC=true ;;
            --validate) DO_VALIDATE=true ;;
            --all)      DO_SYNC=true; DO_VALIDATE=true ;;
            --help|-h)  show_help; exit 0 ;;
            *)          echo -e "${RED}Unknown option: $1${NC}"; show_help; exit 1 ;;
        esac
        shift
    done
fi

# --- Main ---
echo ""

if $DO_SYNC; then
    sync_agents_to_claude
    echo ""
fi

if $DO_VALIDATE; then
    validate_skills
    echo ""
fi

# Final summary
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}Done!${NC}"
$DO_SYNC && echo -e "  CLAUDE.md is up to date"
$DO_VALIDATE && echo -e "  Skills validated"
echo -e "${CYAN}========================================${NC}"
