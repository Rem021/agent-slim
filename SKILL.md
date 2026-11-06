---
name: agent-slim
description: Universal AI Agent & Multi-Stack Workspace Deep Cleaner. Use when the user asks to clean up bloated projects, free disk space across AI agent worktrees (Claude Code, OpenAI Codex, Cursor, Windsurf, Cline, Roo Code, Aider, OpenHands, Devin, Orca, Antigravity), or purge build caches, compiler intermediates, GPU/frame dumps, test artifacts, and stale release builds without losing Git state, uncommitted code, active tasks, referenced assets, or AI agent memory/rules.
---

# `agent-slim` — Universal AI Agent & Multi-Stack Workspace Deep Cleaner

AI coding agents frequently spawn parallel git worktrees, run isolated compiler/test matrices, dump intermediate debug probes, and accumulate hundreds of gigabytes of hidden build caches (`target/`, `DerivedData/`, `.next/`, `wandb/`, `Library/`, `.gradle/`, `.terraform/`).

`agent-slim` is a **zero-dependency, 5-layer guardrail disk space reclaimer** designed for **any developer's AI Agent projects** across **7 major technology ecosystems**.

---

## 1. Universal 5-Layer Safety Guardrails (Iron Rules)

Before deleting a single byte, `agent-slim` enforces five non-negotiable protection layers:

1. **Layer 1 — VCS & Uncommitted Work Protection**:
   - Never modifies or deletes `.git`, `.svn`, `.hg`, `.jj`, tracked source files, or uncommitted working tree edits.
2. **Layer 2 — Universal AI Agent Memory, Rules & Context Protection**:
   - Automatically protects agent state, skills, rules, and handoff documentation across **all mainstream AI coding tools**:
     - **Directories**: `.agents/`, `.claude/`, `.codex/`, `.gemini/`, `.cursor/`, `.windsurf/`, `.cline/`, `.roo/`, `.continue/`, `.aider/`, `.openhands/`, `.devin/`, `.orca/`, `.antigravity/`, `docs/`, `reports/`, `research_notes/`, `specs/`, `adr/`, `memory/`, `memories/`, `prompts/`, `skills/`, `plans/`, `fixtures/`, `testdata/`, `__snapshots__/`, `migrations/`.
     - **Files**: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CURSOR.md`, `WINDSURF.md`, `CODEX.md`, `SKILL.md`, `MEMORY.md`, `PROGRESS.md`, `HANDOFF.md`, `STATUS.md`, `PLAN.md`, `TODO.md`, `RULES.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.roorules`, `.continuerules`, `.aider*`, and all package lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`, `Cargo.lock`, `uv.lock`, `poetry.lock`, `Podfile.lock`, `Package.resolved`).
3. **Layer 3 — Active Process & Modification-Age Guardrail (`--min-age-hours`)**:
   - Can skip any build directory or cache modified within the last `N` hours so active background compilations or test runs are never interrupted.
4. **Layer 4 — Context-Verified Build Directory Matching**:
   - Ambiguous directory names are **never deleted blindly**—they are verified against sibling project manifests first:
     - `target/` is only cleaned if `Cargo.toml` (Rust) or `pom.xml` (Maven) exists in the parent directory.
     - `build/` is only cleaned if `build.gradle(.kts)`, `settings.gradle(.kts)`, `pubspec.yaml`, `CMakeCache.txt`, or `build.ninja` is verified.
     - `.build/` is only cleaned if `Package.swift`, `*.xcodeproj`, or SwiftPM build layout is verified.
     - `Library/`, `Temp/`, `Obj/` are only cleaned inside verified Unity projects (`Assets/` + `ProjectSettings/`).
     - `Intermediate/` is only cleaned inside verified Unreal Engine projects (`*.uproject`).
     - `node_modules/` is only cleaned when `--include-node-modules` is passed AND a sibling `package.json` exists.
5. **Layer 5 — Asset Reference Graph, Model Weights & Release Retention**:
   - Automatically protects AI model weights (`.safetensors`, `.gguf`, `.ckpt`, `.onnx`, `.pt`, `.pth`, `.mlx`, `.tflite`).
   - Parses project manifests (`.fcpxml`, JSON pointers) so linked external media or active trial builds are never orphaned.
   - Retains the newest `N` versioned release builds (`--keep-versions 2`) while purging superseded historical builds.

---

## 2. Supported Technology Stacks (7 Ecosystems Out-of-the-Box)

| Ecosystem | Reclaimable Caches & Artifacts Detected Automatically |
| :--- | :--- |
| **1. Web / JS / TS / Full-Stack** | `.next`, `.nuxt`, `.output`, `.svelte-kit`, `.astro`, `.turbo`, `.parcel-cache`, `.vite`, `.angular`, `.docusaurus`, `.vercel`, `.netlify`, `.wrangler`, `storybook-static`, `playwright-report`, `test-results`, `.nyc_output`, `.eslintcache`, optional `node_modules` (`--include-node-modules`) |
| **2. Python / AI / ML / Data Science** | `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.pytype`, `.hypothesis`, `.tox`, `.nox`, `.ipynb_checkpoints`, `.gradio`, `lightning_logs`, `multirun` (Hydra), `wandb/` (local run caches), `.pyc`/`.pyo` *(while protecting `.safetensors`, `.gguf`, `.pt`, `.ckpt`, `.onnx`)* |
| **3. Systems / Rust / Go / C / C++ / Zig** | Cargo `target/` (verified by `Cargo.toml`), `CMakeFiles`, `cmake-build-*`, `bazel-*`, `.zig-cache`, `zig-out`, `ccache`/`sccache`, `.o`, `.obj`, `.lo`, `.dia`, `.pch`, `.gch`, `.core`/`.dmp` crash dumps, `.profraw`/`.profdata` |
| **4. Mobile & Desktop Native** | Xcode `DerivedData`, SwiftPM `.build`, `ModuleCache.noindex`, `Index.noindex`, `.xcresult`, `.dSYM`, `.trace`, Android `.gradle`, `.kotlin`, `.cxx`, Gradle/Flutter `build/`, `.dart_tool`, React Native `.expo`, unavailable iOS Simulators (`--clean-simulators`) |
| **5. Game Engines** | **Unity** (`Library/`, `Temp/`, `Obj/`, `Logs/` verified by `Assets/` + `ProjectSettings/`), **Unreal Engine** (`Intermediate/`, `DerivedDataCache/`, `Saved/Logs`, `Saved/Crashes` verified by `*.uproject`), **Godot** (`.godot/`) |
| **6. DevOps / Cloud / IaC** | Terraform `.terraform`, `.terragrunt-cache`, Serverless `.serverless`, AWS SAM `.aws-sam` |
| **7. Media / Creative / Graphics** | Final Cut Pro `.fcpbundle` (`Render Files`, `Transcoded Media`, `Analysis Files`), Blender `.blend1`/`.blend2`, uncompressed GPU framebuffer dumps (`.rgba16f`, `.rgba32f`, debug `.raw`), and SHA-256 content-deduplicated scratch copies (`--dedup-scratch-mb`) |

---

## 3. Standard Agent Workflow

### Step 1: Safe Dry-Run Audit (Default)
Always run `agent-slim` in dry-run mode first to inspect the categorized space breakdown and verify which safety guardrails triggered:

```bash
python3 ~/.agents/skills/agent-slim/scripts/agent_slim.py /path/to/workspace
```

### Step 2: Execute Cleanup
Once the dry-run report is confirmed, pass `--execute` to reclaim disk space:

```bash
python3 ~/.agents/skills/agent-slim/scripts/agent_slim.py /path/to/workspace --execute
```

### Step 3: Advanced Multi-Worktree & Archival Cleanup
For sweeping an entire parent directory of AI agent worktrees (e.g., `~/Projects`, `~/.orca/worktrees`, `~/Codex`):

```bash
python3 ~/.agents/skills/agent-slim/scripts/agent_slim.py ~/Projects \
  --include-node-modules \
  --min-age-hours 2 \
  --keep-versions 2 \
  --dedup-scratch-mb 25 \
  --clean-simulators \
  --report-json /tmp/agent-slim-audit.json \
  --execute
```

---

## 4. CLI Reference

| Flag | Default | Description |
| :--- | :--- | :--- |
| `paths...` | *(Required)* | One or more project, worktree, or workspace root directories to scan |
| `--execute` | `False` (Dry-Run) | Perform actual file/directory deletion |
| `--include-node-modules` | `False` | Also remove reinstallable `node_modules/` (verified by sibling `package.json`) |
| `--keep-versions N` | `2` | Retain top `N` newest versioned release builds per prefix group |
| `--min-age-hours H` | `0.0` | Skip any directory/file modified within the last `H` hours (protects active builds) |
| `--dedup-scratch-mb MB` | `25.0` | Fast SHA-256 deduplication of identical large files (`>= MB`) inside scratch/temp/test folders (`0` to disable) |
| `--clean-simulators` | `False` | Run `xcrun simctl delete unavailable` on macOS to remove orphaned iOS Simulator runtimes |
| `--report-json PATH` | `None` | Export a detailed JSON audit report of all candidates, sizes, and protected items |
