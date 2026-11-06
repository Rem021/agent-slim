#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SKILL_DIR}/scripts/agent_slim.py"

chmod +x "${SCRIPT_PATH}"

# 1. Install CLI symlink in ~/.local/bin
mkdir -p "${HOME}/.local/bin"
ln -sf "${SCRIPT_PATH}" "${HOME}/.local/bin/agent-slim"
echo "✅ Installed CLI: ${HOME}/.local/bin/agent-slim -> ${SCRIPT_PATH}"

# 2. Register skill across AI Agent skill directories
AGENT_SKILL_DIRS=(
  "${HOME}/.agents/skills"
  "${HOME}/.claude/skills"
  "${HOME}/.codex/skills"
  "${HOME}/Library/Application Support/orca/antigravity-chat/config/skills"
  "${HOME}/Library/Application Support/orca/antigravity-chat/antigravity-cli/skills"
)

for dir in "${AGENT_SKILL_DIRS[@]}"; do
  if [ -d "$(dirname "${dir}")" ]; then
    mkdir -p "${dir}"
    target="${dir}/agent-slim"
    if [ "${target}" != "${SKILL_DIR}" ]; then
      rm -rf "${target}"
      ln -sf "${SKILL_DIR}" "${target}"
      echo "✅ Registered Agent Skill: ${target} -> ${SKILL_DIR}"
    fi
  fi
done

echo "🎉 agent-slim installation complete! Run 'agent-slim --help' to get started."
