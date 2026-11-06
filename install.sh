#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$REPO_DIR/scripts/agent_slim.py"

# 1. Install CLI binary symlink into ~/.local/bin
mkdir -p "$HOME/.local/bin"
ln -sfn "$REPO_DIR/scripts/agent_slim.py" "$HOME/.local/bin/agent-slim"
echo "[✓] Installed CLI: $HOME/.local/bin/agent-slim"

# 2. Register Universal Agent Skill across mainstream AI Coding Agents
AGENT_SKILL_DIRS=(
  "$HOME/.agents/skills"
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.cursor/skills"
  "$HOME/.windsurf/skills"
)

for skill_root in "${AGENT_SKILL_DIRS[@]}"; do
  mkdir -p "$skill_root"
  target_link="$skill_root/agent-slim"
  if [ "$target_link" != "$REPO_DIR" ]; then
    ln -sfn "$REPO_DIR" "$target_link"
    echo "[✓] Linked Agent Skill: $target_link -> $REPO_DIR"
  fi
done

echo ""
echo "=================================================================="
echo "  agent-slim v2.0.0 installed successfully!"
echo "  Run: agent-slim --help"
echo "=================================================================="
