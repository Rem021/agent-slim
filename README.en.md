# Agent-Slim: Multi-Stack & AI Workspace Deep Cleaner

[![简体中文](https://img.shields.io/badge/Language-简体中文-0969da?style=flat)](./README.zh-CN.md)
[![Version](https://img.shields.io/badge/Version-v2.0.0-1a7f37?style=flat)](https://github.com/Rem021/agent-slim/releases/tag/v2.0.0)
[![Platform](https://img.shields.io/badge/Platform-macOS_%7C_Linux-0969da?style=flat)](https://github.com/Rem021/agent-slim)
[![Safety](https://img.shields.io/badge/Safety-5_Hard_Gates-8250df?style=flat)](#1-five-stage-safety-pipeline)
[![License](https://img.shields.io/badge/License-MIT-656d76?style=flat)](./LICENSE)

> **Switch Language**: [**👉 点击切换至简体中文完整版 (`README.zh-CN.md`)**](./README.zh-CN.md)

**Agent-Slim** is a zero-dependency workspace cleaner designed for developers running parallel AI coding agents and multi-language projects. It reclaims tens of gigabytes of compiler intermediates, stale release archives, and abandoned agent logs while strictly protecting uncommitted source code, active agent memory, and referenced project assets.

---

## 1. Five-Stage Safety Pipeline

Every directory is evaluated through five sequential safety gates before any cleanup action is allowed:

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/safety-pipeline-en-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./assets/safety-pipeline-en-light.svg">
    <img alt="Agent-Slim Five-Stage Safety Pipeline" src="./assets/safety-pipeline-en-light.svg" width="100%">
  </picture>
</p>

| Gate | Protection Rule | Verification Method |
| :--- | :--- | :--- |
| **Gate 01** | Active Process Lock | Skips any workspace with running builds, tests, or open file descriptors (`lsof`). |
| **Gate 02** | Git Worktree Guard | Protects uncommitted edits, staged changes, untracked source files, and stashes (`git status --porcelain`). |
| **Gate 03** | Agent Session Guard | Preserves active tasks, rule files, and conversation contexts Modified within the safety window. |
| **Gate 04** | Asset Reference Graph | Scans source and documentation files to ensure referenced images, models, and fixtures are never removed. |
| **Gate 05** | Latest Release Retention | Retains the newest runnable release artifact per project while purging older build archives. |

---

## 2. Supported Stacks & Agent Workspaces

| Category | Supported Targets | Cleaned Artifacts | Protected State |
| :--- | :--- | :--- | :--- |
| **AI Coding Agents** | Claude Code, Codex, Cursor, Windsurf, Cline, Orca, Antigravity | Expired trace logs, orphaned browser caches, abandoned worktree build dirs | Active conversations, rules (`CLAUDE.md`, `AGENTS.md`), skill definitions |
| **Apple & Mobile** | Xcode, SwiftPM, CocoaPods, React Native, Flutter | `DerivedData`, `.build`, intermediate symbol caches, old `.xcarchive` bundles | Source trees, `.xcodeproj`, signing profiles, latest release archive |
| **Systems & Native** | Rust (`Cargo`), C/C++ (`CMake`), Go, Zig | `target/debug`, `cmake-build-*`, object files, shader compilation caches | `Cargo.lock`, source headers, prebuilt vendor libraries |
| **Web & Python** | Node (`pnpm`, `npm`, `bun`), Next.js, Vite, Python (`uv`, `pytest`) | `.next/cache`, `.turbo`, `__pycache__`, `.pytest_cache`, `.mypy_cache` | Lockfiles, `.env*`, database files (`.sqlite`, `.db`), virtualenvs in active use |

---

## 3. Quick Start

### Audit Mode (Read-Only Preview)

Run a full read-only scan across your workspace directory to inspect reclaimable space without deleting any files:

```bash
python3 scripts/agent_slim.py scan --root ~/Projects
```

### Safe Cleanup Execution

Execute cleanup after reviewing the audit report (enforces all 5 safety gates automatically):

```bash
python3 scripts/agent_slim.py clean --root ~/Projects --keep-latest-release 1
```

### JSON Report for Automation

Export a structured report for CI or scheduled maintenance scripts:

```bash
python3 scripts/agent_slim.py scan --root ~/Projects --json > report.json
```

---

## 4. Repository Layout

```text
agent-slim/
├── SKILL.md                  # Agent skill specification & invocation guide
├── scripts/
│   └── agent_slim.py         # Zero-dependency 5-gate scanner & cleaner
├── assets/                   # Theme-adaptive SVG diagrams (Dark & Light)
├── README.md                 # English documentation (default)
└── README.zh-CN.md           # Simplified Chinese documentation
```

---

## 5. License

Released under the [MIT License](./LICENSE).
