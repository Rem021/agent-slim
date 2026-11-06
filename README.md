# 🧹 agent-slim

**Universal AI Agent & Multi-Stack Workspace Deep Cleaner**  
*Reclaim hundreds of gigabytes of build caches, GPU/frame dumps, VM rootfs images, and duplicate agent worktree artifacts — with 100% preservation of source code, Git history, active tasks, referenced media, and agent memory.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)](#)
[![Agent Skill Ready](https://img.shields.io/badge/Agent_Skill-Codex_%7C_Claude_%7C_Orca_%7C_Antigravity-purple.svg)](#install-as-an-ai-agent-skill)

---

## Why `agent-slim`?

Modern AI-assisted engineering with **Codex**, **Claude Code**, **Orca**, **Antigravity**, and **Cursor** spawns dozens of parallel git worktrees, automated test harnesses, GPU/frame comparisons, simulator backups, and VM runs. Within weeks, a project drive can balloon past **1 TB+** — yet conventional cleaners (`git clean -fdx`, `rm -rf`) are dangerous because they:

1. **Wipe Agent Memory & Handoff Context**: Deleting local `reports/`, `research_notes/`, `RUN_STATE.json`, or `USER_TRIAL_INSTALL.json` destroys multi-session agent continuity.
2. **Corrupt Active Background Tasks**: Deleting `DerivedData`, QEMU `.cpio` images, or `.fcpbundle` caches while a background agent or host app is running crashes the task.
3. **Break Media & Timeline Links**: Blindly deleting `.mov`, `.tiff`, or `.3fr` files breaks Final Cut Pro `.fcpxml` timelines and camera calibration fixtures.

**`agent-slim`** solves this by combining **multi-stack build cache intelligence**, **live process/open-file locking (`ps` + `lsof`)**, **media reference parsing**, and **strict agent-memory whitelisting** in a single zero-dependency tool and Agent Skill.

---

## Key Features & Safety Guarantees

### 🛡️ Five Core Safety Invariants
1. **Active Process & Open-File Guard (`ps` + `lsof`)**
   - Automatically inspects running processes (`xcodebuild`, `swift-frontend`, `qemu`, `simctl`, `Final Cut Pro`, `DaVinci Resolve`, `cargo`, `python`, `node`) and locks any workspace or subdirectory currently in use.
2. **100% Agent Memory & Handoff Preservation**
   - Strictly protects `README.md`, `PROGRESS.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `STATUS.md`, `RULES.md`, `GOAL.md`, `docs/`, `reports/`, `research_notes/`, and small JSON/YAML/TXT receipts (`<=256KB`).
3. **100% Git & Source Code Integrity**
   - Never touches `.git` directories, git worktree links, `.bundle` / `.patch` archives, or source code across any language.
4. **Reference-Aware Media & Project Protection**
   - Parses Final Cut Pro `.fcpxml` timelines (`src="file://..."`), `.fcpbundle` libraries (preserving `Original Media` and SQLite databases while cleaning regenerable `Render Files`), `.cube` LUTs, and `fixtures/` directories.
5. **Recent-File Grace Window**
   - Protects files modified within the last **18 hours** (`--min-age-hours 18` by default) so active or freshly completed work is never disturbed.

---

## Multi-Stack Coverage Matrix

`agent-slim` works out-of-the-box across diverse project types:

| Project Type / Stack | What `agent-slim` Cleans | What `agent-slim` Protects |
|---|---|---|
| **Swift / Xcode / iOS / macOS** | `DerivedData`, `.build`, `ModuleCache`, `Index.noindex`, `.xcresult`, `.trace`, `.dSYM`, `SimBackup`, unavailable Xcode simulators | `.xcodeproj`, `Package.swift`, `Sources/`, `Tests/`, active signed `.app` deliveries |
| **Video / Color / FCP / DaVinci** | `.fcpbundle/**/Render Files`, raw GPU/host texture dumps (`.rgba16f`, `.rgba32f`, `.rgba32uint`, `.raw`, `.bin`), unreferenced scratch test exports (`.mov`, `.mp4`, `.tiff`), giant pixel-comparison JSONs (`>256KB`) | `.fcpbundle` databases & `Original Media`, all media referenced by `.fcpxml`, `.cube` LUTs, calibration `fixtures/` |
| **Camera Science / RAW ISP Lab** | Duplicate multi-gigabyte RAW copies (`.3fr`, `.cap`, `.iiq`, `.ari`, `.arw`, `.dng`, `.mxf`) across scratch worktrees, `.negathumb`, `.bnnsir`, `.rgba-f32le` | Canonical RAW sample (keeps the first copy of each unique RAW asset), ISP source code, test reports & metrics |
| **Embedded / Firmware / QEMU / C++** | `CMakeFiles`, `.o`, `.d`, `.pch`, `.core`, duplicate historical trial `.cpio` rootfs images in `runs/` & `runtime/` | Base firmware/kernel images, active QEMU session files, `build-receipt.json`, `candidate.json`, device trees (`.dtb`) |
| **Web / Node / TypeScript** | `.next`, `.nuxt`, `.turbo`, `.vite`, `.parcel-cache`, `.eslintcache` | `src/`, `package.json`, lockfiles, active worktree `node_modules` |
| **Python / AI / Data Science** | `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.tox`, `.nox` | `.py`, `.ipynb`, `pyproject.toml`, `requirements.txt`, documentation & reports |
| **Rust / Go / JVM / Android** | Cargo `target/` (when `Cargo.toml` present), `.gradle`, build intermediates | `Cargo.toml`, `go.mod`, `build.gradle`, source trees |

---

## Installation

### Option A: One-Line Install (CLI + All AI Agents Skill)

```bash
git clone https://github.com/Rem021/agent-slim.git ~/.agents/skills/agent-slim
chmod +x ~/.agents/skills/agent-slim/install.sh
~/.agents/skills/agent-slim/install.sh
```

`install.sh` automatically:
- Installs the `agent-slim` CLI into `~/.local/bin/agent-slim`
- Registers the `agent-slim` skill into:
  - `~/.agents/skills/agent-slim`
  - `~/.claude/skills/agent-slim` (Claude Code)
  - `~/.codex/skills/agent-slim` (Codex)
  - Orca / Antigravity skills directories (if present)

### Option B: Standalone Zero-Install Execution

Because `agent_slim.py` uses **only the Python 3 standard library**, you can run it directly on any macOS or Linux machine without installing anything:

```bash
python3 scripts/agent_slim.py /path/to/workspace
```

---

## Usage

### 1. Dry-Run Inspection (Default — Safe Preview)

Running `agent-slim` without `--execute` performs a full scan, checks active process locks and media references, and prints a detailed breakdown of reclaimable space:

```bash
agent-slim /Volumes/WorkDrive/AI/Projects
```

Example output:

```text
🔍 [agent-slim v1.0.0] Scanning 1 root(s)...
   • /Volumes/WorkDrive/AI/Projects
🛡️  Active process guard locked 2 active path(s):
   🔒 /Volumes/WorkDrive/AI/Projects/Mac/work/fx3-color-port-20261027
   🔒 /Volumes/WorkDrive/AI/Data/Phayen-lab/stage6-integration-20261105
🎬 Referenced media & project guard locked 75 media/project asset(s).

========================================================================================
📊 agent-slim Report — Mode: DRY-RUN (PREVIEW ONLY — pass --execute to delete)
========================================================================================
  Reclaimable / Deleted :   395,197 files  |   192.96 GiB ( 206.30 GB)
  Protected / Retained  :   169,289 files  |     3.01 GiB (   3.23 GB)
----------------------------------------------------------------------------------------
    80.15 GiB (  86.06 GB)  [   2,498 files]  7. 历史测试批次导出的对比视频/全尺寸图像/临时压缩包 (.mov / .tiff / .png / .zip)
    67.46 GiB (  72.43 GB)  [   4,590 files]  3. 原始 GPU/宿主帧转储与二进制中间产物 (.rgba16f / .rgba32f / .raw / .bin / .o 等)
    19.09 GiB (  20.49 GB)  [  84,346 files]  8. 巨型逐像素/图块数值转储 JSON (>256KB)
    18.69 GiB (  20.07 GB)  [  44,953 files]  2. 编译与构建缓存 (DerivedData / .build / .xcresult / .trace / SimBackup / __pycache__)
========================================================================================
```

### 2. Execute Deep Cleanup & Save JSON Audit Receipt

```bash
agent-slim /Volumes/WorkDrive/AI \
  --execute \
  --clean-simulators \
  --report-json ./reports/agent-slim-audit.json
```

### 3. CLI Reference

| Flag | Default | Description |
|---|---|---|
| `paths...` | `.` | One or more project or workspace root directories to scan |
| `--execute` | `False` | Perform actual deletion and empty-directory pruning (default is dry-run) |
| `--min-age-hours <H>` | `18.0` | Grace window in hours: protect files modified within the last `H` hours |
| `--all-ages` | `False` | Ignore the modification-time grace window (still enforces active process locks) |
| `--large-json-kb <KB>` | `256` | Size threshold in KB for cleaning giant pixel/tile dump JSONs inside scratch dirs |
| `--protect <PATTERN>` | `[]` | Substring or path pattern to explicitly protect (repeatable) |
| `--clean-simulators` | `False` | Also run `xcrun simctl delete unavailable` when `--execute` is active |
| `--report-json <FILE>` | `None` | Write a machine-readable JSON audit receipt with per-category stats and samples |

---

## Repository Structure

```text
agent-slim/
├── SKILL.md                  # AI Agent Skill definition (Claude Code / Codex / Orca / Antigravity)
├── README.md                 # Comprehensive bilingual documentation
├── LICENSE                   # MIT License
├── install.sh                # One-click installer for CLI (~/.local/bin) & Agent Skill symlinks
└── scripts/
    └── agent_slim.py         # Zero-dependency Python 3 universal cleaner engine
```

---

## License

Released under the [MIT License](LICENSE).
