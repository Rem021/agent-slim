---
name: agent-slim
description: Universal AI Agent & Multi-Stack Workspace Deep Cleaner. Use when the user asks to clean up bloated projects, free disk space across AI agent worktrees (Codex, Claude Code, Orca, Antigravity, Cursor), or purge build caches, GPU/frame dumps, duplicate test exports, and stale experiment artifacts without losing project progress, Git state, active tasks, referenced media, or agent memory/documentation.
---

# Agent-Slim: Universal AI Agent & Multi-Stack Deep Cleaner

`agent-slim` is a zero-dependency, process-aware, memory-preserving deep cleanup engine designed for multi-agent development environments and heterogeneous project stacks.

## When to Use This Skill

Trigger `agent-slim` whenever the user asks to:
- Deep-clean a bloated project or entire AI workspace drive
- Reclaim disk space across agent worktrees (`Codex`, `Claude`, `Orca`, `Antigravity`)
- Purge build caches (`DerivedData`, `.build`, `target`, `.next`, `.turbo`, `__pycache__`, `.gradle`, `CMakeFiles`)
- Remove massive GPU/host frame dumps (`.rgba16f`, `.rgba32f`, `.raw`, `.bin`), VM test images (`.cpio`), or duplicate test exports (`.mov`, `.tiff`, `.png`)
- Clean up without affecting development progress, active background tasks, or historical agent memory

---

## Five Core Safety Invariants (Never Violated)

1. **Active Process & Open-File Guard (`ps` + `lsof`)**
   - Automatically detects running processes (`xcodebuild`, `swift-frontend`, `qemu`, `simctl`, `Final Cut Pro`, `Resolve`, `cargo`, `python`, `node`) and locks any workspace or experiment directory currently in use.
2. **100% Agent Memory & Handoff Preservation**
   - Always preserves `README.md`, `PROGRESS.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `STATUS.md`, `RULES.md`, `GOAL.md`, `docs/`, `reports/`, `research_notes/`, and small JSON/YAML/TXT receipts (`RUN_STATE.json`, `USER_TRIAL_INSTALL.json`, `provenance.json`, `verification.json`).
3. **100% Git & Source Code Integrity**
   - Never modifies or deletes `.git` directories, worktree metadata, `.bundle` / `.patch` archives, or tracked source files.
4. **Reference-Aware Media & Project Protection**
   - Parses Final Cut Pro `.fcpxml` timelines (`src="file://..."`), `.fcpbundle` libraries (preserving `Original Media` and SQLite databases while cleaning regenerable `Render Files`), `.cube` LUTs, and `fixtures/` directories so original source media is never touched.
5. **Recent-File Grace Window**
   - By default, protects any file modified within the last **18 hours** (`--min-age-hours 18`) so ongoing or recently finished work is untouched unless `--all-ages` is explicitly requested.

---

## Supported Project Stacks

| Stack / Domain | Regenerable Caches & Intermediates Cleaned | Protected Core Assets |
|---|---|---|
| **Swift / Xcode / iOS / macOS** | `DerivedData`, `.build`, `ModuleCache`, `Index.noindex`, `.xcresult`, `.trace`, `.dSYM`, `SimBackup`, unavailable simulators | `.xcodeproj`, `.xcworkspace`, `Package.swift`, `Sources/`, `Tests/`, active `.app` deliveries |
| **Media / FCP / DaVinci / Camera Lab** | `.fcpbundle/**/Render Files`, raw GPU/texture dumps (`.rgba16f`, `.rgba32f`, `.rgba32uint`, `.raw`, `.bin`, `.negathumb`), duplicate scratch exports (`.mov`, `.tiff`), duplicate scratch RAW copies (`.3fr`, `.cap`, `.mxf`), giant pixel-dump JSONs (`>256KB`) | `.fcpbundle` databases & `Original Media`, `.fcpxml` referenced media, `.cube` LUTs, `fixtures/`, first canonical RAW sample |
| **Rust / C / C++ / Embedded / QEMU** | Cargo `target/`, `CMakeFiles`, `.o`, `.d`, `.pch`, `.core`, duplicate historical trial `.cpio` rootfs images in `runs/` / `runtime/` | `Cargo.toml`, `CMakeLists.txt`, `src/`, base firmware/kernel images, active QEMU session files, `build-receipt.json` |
| **Web / Node / TypeScript** | `.next`, `.nuxt`, `.turbo`, `.vite`, `.parcel-cache`, `.eslintcache` | `src/`, `package.json`, `pnpm-lock.yaml`, active worktree `node_modules` |
| **Python / AI / Data Science** | `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.tox`, scratch tensor dumps | `.py`, `.ipynb`, `pyproject.toml`, `requirements.txt`, model weights in active directories |
| **Multi-Agent Worktrees (`Codex` / `Claude` / `Orca`)** | Stale worktree build caches, duplicate repo snapshots (`actual-full/`, `before/`, `after/`), retired staging caches | Active worktrees, `.git` links, `reports/`, `docs/`, `.bundle` & `.patch` backups |

---

## Quick Start & CLI Usage

### 1. Dry-Run Preview (Default — Zero Deletions)

Always run a dry-run first or when the user wants to inspect space usage:

```bash
python3 ~/.agents/skills/agent-slim/scripts/agent_slim.py /path/to/project_or_workspace
```

### 2. Execute Cleanup & Save Audit Receipt

When authorized to clean:

```bash
python3 ~/.agents/skills/agent-slim/scripts/agent_slim.py \
  /path/to/project_or_workspace \
  --execute \
  --clean-simulators \
  --report-json /path/to/project_or_workspace/reports/agent-slim-receipt.json
```

### 3. CLI Options Reference

- `paths`: One or more directories to scan (e.g., `/Volumes/KAFU2T/AI` or `.`).
- `--execute`: Perform actual file deletions and prune empty directories (without this flag, runs in read-only dry-run mode).
- `--min-age-hours <float>`: Protect files modified within the last N hours (default: `18.0`).
- `--all-ages`: Clean matched caches/dumps regardless of modification time (still enforces active process locks).
- `--large-json-kb <int>`: Threshold in KB for cleaning giant pixel/tile dump JSONs inside scratch directories (default: `256`).
- `--protect <pattern>`: Additional path substring to protect (can be passed multiple times).
- `--clean-simulators`: Also run `xcrun simctl delete unavailable` during `--execute`.
- `--report-json <path>`: Output a detailed JSON audit report with per-category byte counts and sample paths.
