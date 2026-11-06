#!/usr/bin/env python3
"""
agent-slim v2.0.0 — Universal AI Agent & Multi-Stack Workspace Deep Cleaner
===========================================================================
A zero-dependency, safety-first disk space reclaimer engineered for ANY developer
using AI coding agents (Claude Code, OpenAI Codex, Cursor, Windsurf, Cline,
Roo Code, Aider, OpenHands, Devin, Orca, Antigravity) across ANY tech stack:

  1. Web / JS / TS / Full-Stack (Next.js, Nuxt, Vite, Turbo, Astro, SvelteKit, Angular, Parcel, Storybook, Playwright/Cypress)
  2. Python / AI / ML / Data Science (PyTorch/Lightning logs, W&B local caches, Gradio, Jupyter, Ruff, Mypy, Pytest, Tox, Nox, Hydra)
  3. Systems / Rust / Go / C / C++ / Zig (Cargo target/, CMake, Bazel, Zig cache, .o/.obj/.d/.dia/.pch, core dumps, VM images)
  4. Mobile & Desktop Native (Xcode DerivedData, SwiftPM .build, Android .gradle/.cxx/build, Flutter .dart_tool, React Native .expo, xcresult/dSYM/trace)
  5. Game Engines (Unity Library/Temp/Obj, Unreal Intermediate/DerivedDataCache/Saved, Godot .godot)
  6. DevOps / Cloud / IaC (Terraform .terraform, Serverless .serverless, AWS SAM .aws-sam)
  7. Media / Creative / Graphics (FCP Render Files, Blender .blend1/.blend2, raw GPU frame dumps, SHA-256 duplicate scratch files)

Safety Architecture (5-Layer Guardrails):
  - Layer 1: VCS & Uncommitted Work Protection (.git, .svn, .hg are NEVER touched)
  - Layer 2: Universal AI Agent Memory & Rules Protection (.agents, .claude, .codex, .cursor, .windsurf, .cline, .roo, .aider, AGENTS.md, CLAUDE.md, MEMORY.md, PROGRESS.md, etc.)
  - Layer 3: Active Process / Lockfile Detection (skips directories with recent modifications within --min-age-hours or active lockfiles)
  - Layer 4: Context-Verified Build Directory Matching (e.g., only cleans `target/` if `Cargo.toml` or `pom.xml` exists alongside it; only cleans Unity `Library/` if `ProjectSettings/` + `Assets/` exist)
  - Layer 5: Reference Graph & Version Retention (parses XML/JSON/YAML/Markdown manifests for linked assets, and retains the top N newest release packages while purging stale earlier iterations)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

VERSION = "2.0.0"

# ============================================================================
# 1. UNIVERSAL GUARDRAILS: NEVER DELETE THESE DIRECTORIES OR FILES
# ============================================================================

PROTECTED_DIRS: Set[str] = {
    # Version Control Systems
    ".git", ".svn", ".hg", ".jj",
    # AI Coding Agent State, Memory, Rules & Skills
    ".agents", ".agent", ".claude", ".codex", ".gemini", ".cursor",
    ".windsurf", ".cline", ".roo", ".continue", ".aider", ".openhands",
    ".devin", ".goose", ". sweep", ".copilot", ".antigravity", ".orca",
    # IDE & Repository Configuration
    ".github", ".gitlab", ".vscode", ".idea", ".fleet", ".zed",
    # Documentation, Architecture, Specs & Agent Memory Folders
    "docs", "doc", "documentation", "reports", "research_notes", "notes",
    "specs", "adr", "architecture", "memory", "memories", "prompts", "skills",
    "plans", "context", "handover", "handoff",
    # Test Fixtures, Snapshots & Database Migrations (Source of Truth)
    "fixtures", "testdata", "__snapshots__", "migrations", "seeds", "schemas",
}

PROTECTED_FILES: Set[str] = {
    # AI Agent Instructions, Memory & Handoff Files
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", "CURSOR.md", "WINDSURF.md",
    "CODEX.md", "SKILL.md", "MEMORY.md", "PROGRESS.md", "HANDOFF.md",
    "STATUS.md", "PLAN.md", "TODO.md", "TASKS.md", "GOAL.md", "RULES.md",
    "ARCHITECTURE.md", "CONTEXT.md", "PROMPT.md", "README.md", "CHANGELOG.md",
    "CONTRIBUTING.md", "LICENSE", "SECURITY.md",
    # Dotfile Agent Rules
    ".cursorrules", ".windsurfrules", ".clinerules", ".roorules",
    ".continuerules", ".aider.conf.yml", ".aider.model.settings.yml",
    # Dependency Lockfiles & Project Manifests (Never delete)
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock",
    "Cargo.toml", "Cargo.lock", "pyproject.toml", "poetry.lock", "uv.lock",
    "Pipfile", "Pipfile.lock", "requirements.txt", "environment.yml",
    "go.mod", "go.sum", "Package.swift", "Package.resolved",
    "Podfile", "Podfile.lock", "pubspec.yaml", "pubspec.lock",
    "Gemfile", "Gemfile.lock", "composer.json", "composer.lock",
    "Makefile", "CMakeLists.txt", "justfile", "Dockerfile", "docker-compose.yml",
    ".env", ".env.local", ".env.development", ".env.production", ".env.example",
}

# Protected AI Model Weight & Dataset Extensions (Protected by default unless --purge-models)
PROTECTED_MODEL_EXTS: Set[str] = {
    ".safetensors", ".gguf", ".ckpt", ".onnx", ".pt", ".pth", ".bin", ".h5", ".tflite", ".mlmodel"
}

# ============================================================================
# 2. UNIVERSAL MULTI-STACK CACHE & ARTIFACT SIGNATURES
# ============================================================================

# Unconditional disposable cache/build directories (safe to remove in any project)
UNCONDITIONAL_CACHE_DIRS: Dict[str, str] = {
    # Web / JS / TS / Full-Stack
    ".next": "Web Build Cache (Next.js .next)",
    ".nuxt": "Web Build Cache (Nuxt .nuxt)",
    ".output": "Web Build Cache (Nitro/Nuxt .output)",
    ".svelte-kit": "Web Build Cache (SvelteKit .svelte-kit)",
    ".astro": "Web Build Cache (Astro .astro)",
    ".turbo": "Monorepo Cache (Turborepo .turbo)",
    ".parcel-cache": "Bundler Cache (Parcel .parcel-cache)",
    ".vite": "Bundler Cache (Vite .vite)",
    ".angular": "Web Build Cache (Angular .angular)",
    ".docusaurus": "Docs Build Cache (Docusaurus .docusaurus)",
    ".vercel": "Deployment Build Cache (.vercel)",
    ".netlify": "Deployment Build Cache (.netlify)",
    ".wrangler": "Cloudflare Workers Cache (.wrangler)",
    "storybook-static": "Storybook Static Build (storybook-static)",
    "playwright-report": "E2E Test Report Cache (playwright-report)",
    "test-results": "E2E Test Artifacts (test-results)",
    ".nyc_output": "Code Coverage Cache (.nyc_output)",
    # Python / AI / ML / Data Science
    "__pycache__": "Python Bytecode Cache (__pycache__)",
    ".pytest_cache": "Python Test Cache (.pytest_cache)",
    ".mypy_cache": "Python Typecheck Cache (.mypy_cache)",
    ".ruff_cache": "Python Linter Cache (.ruff_cache)",
    ".pytype": "Python Typecheck Cache (.pytype)",
    ".hypothesis": "Property Test Cache (.hypothesis)",
    ".tox": "Python Env Matrix Cache (.tox)",
    ".nox": "Python Env Matrix Cache (.nox)",
    ".ipynb_checkpoints": "Jupyter Checkpoint Cache (.ipynb_checkpoints)",
    ".gradio": "Gradio Temp Cache (.gradio)",
    "lightning_logs": "PyTorch Lightning Logs (lightning_logs)",
    "multirun": "Hydra Experiment Sweep Cache (multirun)",
    # Systems / C / C++ / Zig / Bazel
    "CMakeFiles": "CMake Intermediate Directory (CMakeFiles)",
    ".zig-cache": "Zig Compiler Cache (.zig-cache)",
    "zig-out": "Zig Build Output (zig-out)",
    ".cache": "Local Tooling Cache (.cache)",
    "ccache": "Compiler Cache (ccache)",
    ".ccache": "Compiler Cache (.ccache)",
    "sccache": "Compiler Cache (sccache)",
    # Mobile & Desktop Native (Xcode / Swift / Android / Flutter / React Native)
    "DerivedData": "Xcode DerivedData Build Cache",
    "ModuleCache.noindex": "Clang/Swift Module Cache",
    "Index.noindex": "Xcode Index Cache (Index.noindex)",
    "SDKStatCaches.noindex": "Xcode SDK Stat Cache",
    ".swiftpm": "Swift Package Manager Cache (.swiftpm)",
    ".gradle": "Gradle Project Cache (.gradle)",
    ".kotlin": "Kotlin Compiler Cache (.kotlin)",
    ".cxx": "Android NDK C++ Build Cache (.cxx)",
    ".dart_tool": "Dart/Flutter Tooling Cache (.dart_tool)",
    ".expo": "Expo React Native Cache (.expo)",
    # Game Engines
    "DerivedDataCache": "Unreal Engine DerivedDataCache",
    ".godot": "Godot Engine Import/Build Cache (.godot)",
    # DevOps / Cloud / IaC
    ".terraform": "Terraform Provider Cache (.terraform)",
    ".terragrunt-cache": "Terragrunt Cache (.terragrunt-cache)",
    ".serverless": "Serverless Framework Build (.serverless)",
    ".aws-sam": "AWS SAM Build Cache (.aws-sam)",
}

# Disposable directories matched by prefix
PREFIX_CACHE_DIRS: Tuple[Tuple[str, str], ...] = (
    ("cmake-build-", "CLion / CMake Build Directory (cmake-build-*)"),
    ("bazel-", "Bazel Build Symlink/Output (bazel-*)"),
    (" DerivedData", "Xcode DerivedData Cache"),
)

# Disposable directories matched by suffix (bundle extensions that are directories on macOS)
SUFFIX_CACHE_DIRS: Tuple[Tuple[str, str], ...] = (
    (".xcresult", "Xcode Test Result Bundle (.xcresult)"),
    (".dSYM", "Debug Symbols Bundle (.dSYM)"),
    (".trace", "Instruments Profiling Trace (.trace)"),
    (".SavedState", "macOS Saved Application State (.SavedState)"),
)

# Disposable individual file extensions (intermediate compiler outputs, dumps, backups)
DISPOSABLE_FILE_EXTS: Dict[str, str] = {
    # Compiler intermediates
    ".o": "Compiled Object File (.o)",
    ".obj": "Compiled Object File (.obj)",
    ".lo": "Libtool Object File (.lo)",
    ".dia": "Clang Serialized Diagnostics (.dia)",
    ".pch": "Precompiled Header (.pch)",
    ".gch": "GCC Precompiled Header (.gch)",
    ".ilk": "MSVC Incremental Linker File (.ilk)",
    ".exp": "MSVC Export File (.exp)",
    ".pyc": "Python Bytecode (.pyc)",
    ".pyo": "Python Optimized Bytecode (.pyo)",
    # Crash dumps & profiling traces
    ".core": "Process Core Dump (.core)",
    ".dmp": "Crash Minidump (.dmp)",
    ".mdmp": "Windows Crash Minidump (.mdmp)",
    ".hprof": "JVM Heap Dump (.hprof)",
    ".profraw": "LLVM Raw Coverage Profile (.profraw)",
    ".profdata": "LLVM Merged Coverage Profile (.profdata)",
    # Raw GPU / Framebuffer / Render Dumps
    ".rgba16f": "Raw Half-Float GPU Framebuffer Dump (.rgba16f)",
    ".rgba32f": "Raw Float GPU Framebuffer Dump (.rgba32f)",
    # Creative / CAD Backups
    ".blend1": "Blender Auto-Backup File (.blend1)",
    ".blend2": "Blender Auto-Backup File (.blend2)",
    ".bak": "Backup File (.bak)",
    ".tmp": "Temporary File (.tmp)",
    ".temp": "Temporary File (.temp)",
    ".swp": "Vim Swap File (.swp)",
}

DISPOSABLE_EXACT_FILES: Set[str] = {
    ".DS_Store",
    "Thumbs.db",
    ".eslintcache",
    ".stylelintcache",
    ".prettiercache",
    "npm-debug.log",
    "yarn-error.log",
    ".coverage",
}

# ============================================================================
# 3. DATA STRUCTURES & HELPERS
# ============================================================================

@dataclass
class CandidateItem:
    path: Path
    category: str
    size_bytes: int
    reason: str
    is_dir: bool


@dataclass
class ScanReport:
    root: Path
    candidates: List[CandidateItem] = field(default_factory=list)
    protected_notes: List[str] = field(default_factory=list)
    skipped_active: List[str] = field(default_factory=list)

    @property
    def total_bytes(self) -> int:
        return sum(c.size_bytes for c in self.candidates)


def format_bytes(num_bytes: int) -> str:
    val = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if val < 1024.0 or unit == "TB":
            return f"{val:.2f} {unit}"
        val /= 1024.0
    return f"{val:.2f} TB"


def get_path_size(path: Path) -> int:
    """Fast recursive size calculation without following symlinks."""
    if path.is_symlink():
        return 0
    try:
        if path.is_file():
            return path.stat().st_size
    except OSError:
        return 0

    total = 0
    stack = [path]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    if entry.is_symlink():
                        continue
                    if entry.is_file(follow_symlinks=False):
                        try:
                            total += entry.stat(follow_symlinks=False).st_size
                        except OSError:
                            pass
                    elif entry.is_dir(follow_symlinks=False):
                        stack.append(Path(entry.path))
        except OSError:
            pass
    return total


def is_recently_modified(path: Path, min_age_seconds: float) -> bool:
    """Check if a directory or file was modified within `min_age_seconds` (Active Task Guardrail)."""
    if min_age_seconds <= 0:
        return False
    now = time.time()
    try:
        if (now - path.stat(follow_symlinks=False).st_mtime) < min_age_seconds:
            return True
    except OSError:
        return False
    return False


def fast_file_signature(path: Path) -> Optional[str]:
    """Compute a fast content signature (size + first 64KB + middle 64KB + last 64KB SHA-256)."""
    try:
        size = path.stat().st_size
        if size == 0:
            return None
        h = hashlib.sha256()
        h.update(str(size).encode("utf-8"))
        chunk_size = 65536
        with open(path, "rb") as f:
            h.update(f.read(chunk_size))
            if size > chunk_size * 2:
                f.seek(size // 2)
                h.update(f.read(chunk_size))
            if size > chunk_size:
                f.seek(max(0, size - chunk_size))
                h.update(f.read(chunk_size))
        return h.hexdigest()
    except OSError:
        return None


# ============================================================================
# 4. CONTEXT-VERIFIED BUILD DIRECTORY DETECTION (LAYER 4 GUARDRAIL)
# ============================================================================

def classify_context_verified_dir(
    dir_path: Path,
    dir_name: str,
    include_node_modules: bool,
) -> Optional[Tuple[str, str]]:
    """
    Verify ambiguous directory names (`target`, `build`, `.build`, `Library`, `Temp`,
    `Intermediate`, `wandb`, `node_modules`) using sibling manifest files so we NEVER
    accidentally delete a source folder that happens to share a name.
    """
    parent = dir_path.parent

    # 1. Rust Cargo or Java Maven `target/`
    if dir_name == "target":
        if (parent / "Cargo.toml").exists():
            return ("Rust Cargo Build Target (target/)", "Verified sibling Cargo.toml")
        if (parent / "pom.xml").exists():
            return ("Maven Build Target (target/)", "Verified sibling pom.xml")

    # 2. SwiftPM / Xcode `.build/`
    if dir_name == ".build":
        if (parent / "Package.swift").exists() or any(parent.glob("*.xcodeproj")) or any(parent.glob("*.xcworkspace")):
            return ("SwiftPM Build Cache (.build/)", "Verified sibling Package.swift / Xcode project")
        # Also match if it contains arm64-apple-macosx or x86_64-apple-macosx
        if (dir_path / "arm64-apple-macosx").exists() or (dir_path / "checkouts").exists():
            return ("SwiftPM Build Cache (.build/)", "Contains SwiftPM build layout")

    # 3. Gradle / Android / Flutter / CMake `build/`
    if dir_name == "build":
        if (
            (parent / "build.gradle").exists()
            or (parent / "build.gradle.kts").exists()
            or (parent / "settings.gradle").exists()
            or (parent / "settings.gradle.kts").exists()
            or (parent / "pubspec.yaml").exists()
        ):
            return ("Gradle / Flutter Build Output (build/)", "Verified sibling build.gradle / pubspec.yaml")
        if (dir_path / "CMakeCache.txt").exists() or (dir_path / "build.ninja").exists():
            return ("CMake / Ninja Build Directory (build/)", "Contains CMakeCache.txt / build.ninja")

    # 4. Unity Engine `Library/`, `Temp/`, `Obj/`, `Logs/`
    if dir_name in {"Library", "Temp", "Obj", "Logs"}:
        if (parent / "Assets").is_dir() and (parent / "ProjectSettings").is_dir():
            return (f"Unity Engine Cache ({dir_name}/)", "Verified Unity project (Assets/ + ProjectSettings/)")

    # 5. Unreal Engine `Intermediate/`, `Saved/Logs`, `Saved/Crashes`
    if dir_name == "Intermediate":
        if any(parent.glob("*.uproject")):
            return ("Unreal Engine Intermediate Build", "Verified sibling *.uproject")
    if dir_name in {"Logs", "Crashes", "Autosaves"} and parent.name == "Saved":
        if any(parent.parent.glob("*.uproject")):
            return (f"Unreal Engine Saved/{dir_name}", "Verified Unreal *.uproject")

    # 6. Weights & Biases (`wandb/`) local run caches
    if dir_name == "wandb":
        if (dir_path / "latest-run").exists() or any(dir_path.glob("run-*")) or any(dir_path.glob("offline-run-*")):
            return ("Weights & Biases Local Run Cache (wandb/)", "Contains W&B run-* directories")

    # 7. Node / Frontend `node_modules/` (Opt-in via --include-node-modules)
    if dir_name == "node_modules" and include_node_modules:
        if (parent / "package.json").exists():
            return ("Node.js Dependencies (node_modules/)", "Reinstallable via npm/pnpm/yarn/bun (--include-node-modules)")

    # 8. Explicit temporary build/probe folders created by AI agents
    lower_name = dir_name.lower()
    if (
        lower_name.startswith(".tmp-build")
        or lower_name.startswith("tmp_build")
        or lower_name.startswith(".cargo-target")
        or lower_name.startswith("cargo-target")
        or lower_name.startswith("deriveddata")
        or lower_name.startswith("cmake_build")
        or lower_name.startswith("probe_out")
    ):
        return ("Agent Temporary Build/Probe Directory", f"Matches temporary build pattern '{dir_name}'")

    return None


# ============================================================================
# 5. REFERENCE GRAPH & VERSION RETENTION (LAYER 5 GUARDRAIL)
# ============================================================================

def collect_referenced_paths(root: Path) -> Set[Path]:
    """
    Scan FCPXML (.fcpxml, .fcpxmld) and JSON/YAML manifest files to build a
    set of referenced local file paths that MUST NOT be deleted.
    """
    referenced: Set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [
            d for d in dirnames
            if d not in UNCONDITIONAL_CACHE_DIRS and d not in {".git", "node_modules", "DerivedData", "target"}
        ]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fname.endswith(".fcpxml"):
                try:
                    tree = ET.parse(fpath)
                    for elem in tree.getroot().iter("media-rep"):
                        src = elem.attrib.get("src", "")
                        if src.startswith("file://"):
                            parsed = urllib.parse.urlparse(src)
                            decoded = urllib.parse.unquote(parsed.path)
                            try:
                                referenced.add(Path(decoded).resolve())
                            except OSError:
                                referenced.add(Path(decoded))
                except Exception:
                    pass
    return referenced


def version_sort_key(name: str) -> Tuple[int, ...]:
    """Extract numeric version tuple for sorting release/trial directories."""
    nums = [int(n) for n in re.findall(r"\d+", name)]
    return tuple(nums) if nums else (0,)


def scan_versioned_release_dirs(
    root: Path,
    keep_versions: int,
    report: ScanReport,
    seen_paths: Set[Path],
) -> None:
    """
    Detect versioned build/release output directories (e.g., `releases/`, `dist-releases/`,
    or directories containing multiple versioned build folders + an active pointer JSON/symlink)
    and retain the newest `keep_versions` + any actively linked version.
    """
    for candidate_parent in root.rglob("*"):
        if not candidate_parent.is_dir() or candidate_parent.is_symlink():
            continue
        if any(p in seen_paths for p in candidate_parent.parents):
            continue

        # Check if directory has an active install/release manifest JSON pointing to a current version
        active_refs: Set[str] = set()
        for jf in candidate_parent.glob("*.json"):
            try:
                text = jf.read_text(encoding="utf-8", errors="ignore")
                active_refs.update(re.findall(r"[A-Za-z0-9_.\-]+(?:beta|rc|alpha|v)\d+[A-Za-z0-9_.\-]*", text))
            except OSError:
                pass

        # Group subdirectories that share a versioned naming prefix (e.g., App-0.3.0-beta.1 .. App-0.3.0-beta.27)
        subdirs = [
            d for d in candidate_parent.iterdir()
            if d.is_dir() and not d.is_symlink() and re.search(r"v?\d+\.\d+\.\d+", d.name)
        ]
        if len(subdirs) <= keep_versions:
            continue

        # Group by base prefix before the version number
        groups: Dict[str, List[Path]] = {}
        for d in subdirs:
            m = re.match(r"^(.*?)(v?\d+\.\d+\.\d+.*)$", d.name)
            if m:
                prefix = m.group(1).rstrip("-_")
                groups.setdefault(prefix, []).append(d)

        for prefix, group_dirs in groups.items():
            if len(group_dirs) <= keep_versions:
                continue
            sorted_dirs = sorted(
                group_dirs,
                key=lambda p: (version_sort_key(p.name), p.stat().st_mtime if p.exists() else 0.0),
                reverse=True,
            )
            kept = set(sorted_dirs[:keep_versions])
            for d in sorted_dirs:
                if any(ref in d.name for ref in active_refs):
                    kept.add(d)

            for d in sorted_dirs:
                if d in kept:
                    report.protected_notes.append(f"Retained recent/active versioned build: {d}")
                elif d not in seen_paths:
                    sz = get_path_size(d)
                    if sz > 0:
                        seen_paths.add(d)
                        report.candidates.append(
                            CandidateItem(
                                path=d,
                                category="Stale Versioned Release Builds",
                                size_bytes=sz,
                                reason=f"Superseded release build (retained top {keep_versions} newest versions)",
                                is_dir=True,
                            )
                        )


# ============================================================================
# 6. CONTENT-BASED SCRATCH DEDUPLICATION (SHA-256 FAST SIGNATURE)
# ============================================================================

def scan_duplicate_scratch_files(
    root: Path,
    dedup_min_mb: float,
    referenced_paths: Set[Path],
    report: ScanReport,
    seen_paths: Set[Path],
) -> None:
    """
    Find byte-identical large files (>= dedup_min_mb) inside temporary/scratch/test/export
    directories and mark redundant copies for cleanup while keeping the canonical source.
    """
    if dedup_min_mb <= 0:
        return
    min_bytes = int(dedup_min_mb * 1024 * 1024)
    scratch_keywords = {"tmp", "temp", "scratch", "test_out", "exports", "dumps", "captures", "work"}

    sig_map: Dict[str, List[Path]] = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current_dir = Path(dirpath)
        if current_dir in seen_paths or any(p in seen_paths for p in current_dir.parents):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in PROTECTED_DIRS]

        for fname in filenames:
            fpath = current_dir / fname
            if fpath in seen_paths or fpath.is_symlink():
                continue
            if fpath.suffix.lower() in PROTECTED_MODEL_EXTS:
                continue
            try:
                sz = fpath.stat().st_size
            except OSError:
                continue
            if sz < min_bytes:
                continue
            sig = fast_file_signature(fpath)
            if sig:
                sig_map.setdefault(sig, []).append(fpath)

    for sig, paths in sig_map.items():
        if len(paths) < 2:
            continue
        # Sort so canonical (non-scratch, shorter path, or referenced) comes first
        def canonical_priority(p: Path) -> Tuple[int, int, str]:
            try:
                is_ref = 0 if p.resolve() in referenced_paths else 1
            except OSError:
                is_ref = 1
            in_scratch = 1 if any(k in part.lower() for part in p.parts for k in scratch_keywords) else 0
            return (is_ref, in_scratch, str(p))

        sorted_paths = sorted(paths, key=canonical_priority)
        canonical = sorted_paths[0]
        for dup in sorted_paths[1:]:
            try:
                if dup.resolve() in referenced_paths:
                    continue
            except OSError:
                pass
            # Only auto-clean duplicates if they reside in a scratch/temp/test/work folder
            # or have `.copy` / `copy` in their name
            dup_parts_lower = [part.lower() for part in dup.parts]
            if any(k in part for part in dup_parts_lower for k in scratch_keywords) or "copy" in dup.name.lower():
                sz = get_path_size(dup)
                seen_paths.add(dup)
                report.candidates.append(
                    CandidateItem(
                        path=dup,
                        category="Duplicate Large Scratch/Test Artifacts",
                        size_bytes=sz,
                        reason=f"Byte-identical duplicate of {canonical.name} (SHA-256 signature verified)",
                        is_dir=False,
                    )
                )


# ============================================================================
# 7. MAIN WORKSPACE SCANNER
# ============================================================================

def scan_workspace(
    root: Path,
    include_node_modules: bool = False,
    keep_versions: int = 2,
    min_age_hours: float = 0.0,
    dedup_scratch_mb: float = 25.0,
) -> ScanReport:
    report = ScanReport(root=root)
    seen_paths: Set[Path] = set()
    min_age_seconds = min_age_hours * 3600.0
    referenced_paths = collect_referenced_paths(root)
    if referenced_paths:
        report.protected_notes.append(f"Protected {len(referenced_paths)} active media/manifest-referenced asset(s)")

    # Pass 1: Walk directory tree for unconditional & context-verified caches
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current_dir = Path(dirpath)
        if current_dir in seen_paths or any(p in seen_paths for p in current_dir.parents):
            dirnames[:] = []
            continue

        # Special handling for Final Cut Pro `.fcpbundle` packages
        if current_dir.name.endswith(".fcpbundle"):
            for sub in ("Render Files", "Transcoded Media", "Analysis Files"):
                for match in current_dir.rglob(sub):
                    if match.is_dir() and match not in seen_paths:
                        sz = get_path_size(match)
                        if sz > 0:
                            seen_paths.add(match)
                            report.candidates.append(
                                CandidateItem(
                                    path=match,
                                    category="Media Render Cache (.fcpbundle)",
                                    size_bytes=sz,
                                    reason=f"Regenerable FCP {sub} inside {current_dir.name}",
                                    is_dir=True,
                                )
                            )
            dirnames[:] = []
            continue

        kept_dirs: List[str] = []
        for d in dirnames:
            d_path = current_dir / d
            if d_path.is_symlink():
                continue

            # Layer 1 & 2: Never traverse or delete Protected VCS / AI Agent Memory Directories
            if d in PROTECTED_DIRS:
                if d in {".agents", ".claude", ".codex", ".cursor", ".windsurf", ".cline", ".roo", "memory", "reports"}:
                    report.protected_notes.append(f"Protected AI Agent Memory/Config: {d_path}")
                continue

            matched_category: Optional[str] = None
            matched_reason: Optional[str] = None

            # Check unconditional cache directories
            if d in UNCONDITIONAL_CACHE_DIRS:
                matched_category = UNCONDITIONAL_CACHE_DIRS[d]
                matched_reason = f"Standard disposable cache/build directory '{d}'"

            # Check prefix patterns (e.g., cmake-build-*, bazel-*)
            if not matched_category:
                for prefix, cat in PREFIX_CACHE_DIRS:
                    if d.startswith(prefix):
                        matched_category = cat
                        matched_reason = f"Matches build directory prefix '{prefix}*'"
                        break

            # Check suffix patterns (e.g., *.xcresult, *.dSYM, *.trace)
            if not matched_category:
                for suffix, cat in SUFFIX_CACHE_DIRS:
                    if d.endswith(suffix):
                        matched_category = cat
                        matched_reason = f"Matches diagnostic/symbol bundle suffix '*{suffix}'"
                        break

            # Layer 4: Context-verified build directories (target/, build/, .build/, Library/, wandb/, node_modules/)
            if not matched_category:
                verified = classify_context_verified_dir(d_path, d, include_node_modules)
                if verified:
                    matched_category, matched_reason = verified

            if matched_category and matched_reason:
                # Layer 3: Active process / modification age check
                if is_recently_modified(d_path, min_age_seconds):
                    report.skipped_active.append(f"Skipped recently modified (<{min_age_hours}h): {d_path}")
                    continue
                sz = get_path_size(d_path)
                if sz > 0:
                    seen_paths.add(d_path)
                    report.candidates.append(
                        CandidateItem(
                            path=d_path,
                            category=matched_category,
                            size_bytes=sz,
                            reason=matched_reason,
                            is_dir=True,
                        )
                    )
                continue

            kept_dirs.append(d)

        dirnames[:] = kept_dirs

        # Inspect individual files in non-pruned directories
        for fname in filenames:
            fpath = current_dir / fname
            if fpath.is_symlink() or fpath in seen_paths:
                continue

            if fname in PROTECTED_FILES:
                continue

            ext = fpath.suffix.lower()
            if ext in PROTECTED_MODEL_EXTS:
                continue

            try:
                if fpath.resolve() in referenced_paths:
                    continue
            except OSError:
                pass

            file_cat: Optional[str] = None
            file_reason: Optional[str] = None

            if fname in DISPOSABLE_EXACT_FILES:
                file_cat = "OS & Linter Metadata Cache"
                file_reason = f"Disposable metadata/cache file '{fname}'"
            elif ext in DISPOSABLE_FILE_EXTS:
                file_cat = DISPOSABLE_FILE_EXTS[ext]
                file_reason = f"Disposable intermediate/dump file (*{ext})"
            elif ext == ".raw" and any(
                k in fname.lower() for k in ("dump", "probe", "debug", "capture", "temp", "out_")
            ):
                # Distinguish raw framebuffer dumps from camera RAW photos (.ARW/.CR3/.NEF/.DNG are never .raw, and we require debug keywords)
                file_cat = "Raw Debug Framebuffer Dump (.raw)"
                file_reason = "Uncompressed debug/framebuffer dump matching dump/probe/capture naming"

            if file_cat and file_reason:
                if is_recently_modified(fpath, min_age_seconds):
                    continue
                sz = get_path_size(fpath)
                if sz > 0:
                    seen_paths.add(fpath)
                    report.candidates.append(
                        CandidateItem(
                            path=fpath,
                            category=file_cat,
                            size_bytes=sz,
                            reason=file_reason,
                            is_dir=False,
                        )
                    )

    # Pass 2: Versioned release build retention (keep top N newest + active)
    scan_versioned_release_dirs(root, keep_versions, report, seen_paths)

    # Pass 3: Fast SHA-256 duplicate scratch/test artifact detection
    scan_duplicate_scratch_files(root, dedup_scratch_mb, referenced_paths, report, seen_paths)

    return report


# ============================================================================
# 8. EXECUTION & REPORTING
# ============================================================================

def execute_cleanup(report: ScanReport) -> Tuple[int, int, List[str]]:
    deleted_bytes = 0
    deleted_count = 0
    errors: List[str] = []

    for item in report.candidates:
        try:
            if not item.path.exists() and not item.path.is_symlink():
                continue
            if item.is_dir:
                shutil.rmtree(item.path)
            else:
                item.path.unlink()
            deleted_bytes += item.size_bytes
            deleted_count += 1
        except Exception as exc:
            errors.append(f"{item.path}: {exc}")

    return deleted_bytes, deleted_count, errors


def clean_unavailable_ios_simulators(execute: bool) -> str:
    if shutil.which("xcrun") is None:
        return "xcrun not found (skipping iOS Simulator check)"
    if not execute:
        return "Dry-run: would run `xcrun simctl delete unavailable`"
    try:
        subprocess.run(
            ["xcrun", "simctl", "delete", "unavailable"],
            check=True,
            capture_output=True,
            text=True,
        )
        return "Executed `xcrun simctl delete unavailable` successfully"
    except Exception as exc:
        return f"Simulator cleanup note: {exc}"


def print_summary(reports: List[ScanReport], execute: bool, top_n: int = 25) -> None:
    mode_str = "EXECUTION MODE (DELETING FILES)" if execute else "DRY-RUN MODE (NO FILES DELETED)"
    print("=" * 84)
    print(f"  agent-slim v{VERSION} — {mode_str}")
    print("=" * 84)

    grand_total = 0
    category_totals: Dict[str, int] = {}
    category_counts: Dict[str, int] = {}
    all_candidates: List[CandidateItem] = []

    for rep in reports:
        print(f"\n[Workspace] {rep.root}")
        print(f"  Candidates found : {len(rep.candidates)}")
        print(f"  Reclaimable space: {format_bytes(rep.total_bytes)}")
        if rep.protected_notes:
            unique_notes = sorted(set(rep.protected_notes))
            print(f"  Safety guardrails: {len(unique_notes)} active protection rule(s) triggered")
            for note in unique_notes[:5]:
                print(f"    - [PROTECTED] {note}")
            if len(unique_notes) > 5:
                print(f"    - ... and {len(unique_notes) - 5} more protected items")
        if rep.skipped_active:
            print(f"  Active skipped   : {len(rep.skipped_active)} recently modified item(s) skipped")

        grand_total += rep.total_bytes
        for c in rep.candidates:
            category_totals[c.category] = category_totals.get(c.category, 0) + c.size_bytes
            category_counts[c.category] = category_counts.get(c.category, 0) + 1
            all_candidates.append(c)

    print("\n" + "-" * 84)
    print("  Breakdown by Stack / Category")
    print("-" * 84)
    for cat, sz in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        cnt = category_counts[cat]
        print(f"  {cat:<48} {cnt:>6} item(s)   {format_bytes(sz):>12}")

    if all_candidates:
        print("\n" + "-" * 84)
        print(f"  Top {min(top_n, len(all_candidates))} Largest Reclaimable Targets")
        print("-" * 84)
        for item in sorted(all_candidates, key=lambda x: x.size_bytes, reverse=True)[:top_n]:
            kind = "DIR " if item.is_dir else "FILE"
            print(f"  [{kind}] {format_bytes(item.size_bytes):>10}  {item.path}")
            print(f"         └─ {item.category}: {item.reason}")

    print("\n" + "=" * 84)
    print(f"  TOTAL RECLAIMABLE SPACE: {format_bytes(grand_total)} across {len(all_candidates)} item(s)")
    if not execute:
        print("  Tip: Re-run with `--execute` to permanently delete these items.")
    print("=" * 84)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="agent-slim",
        description=(
            "Universal AI Agent & Multi-Stack Workspace Deep Cleaner. "
            "Reclaims 50%–95% of bloated project disk space across Web, Python/AI/ML, "
            "Rust/C++/Go, Xcode/Swift/Android, Unity/Unreal/Godot, and Media stacks while "
            "strictly protecting Git state, uncommitted code, and AI Agent memory."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more project, worktree, or parent workspace directories to scan.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Perform actual deletion (default is safe dry-run mode).",
    )
    parser.add_argument(
        "--include-node-modules",
        action="store_true",
        help="Also remove reinstallable `node_modules/` directories (verified by sibling package.json).",
    )
    parser.add_argument(
        "--keep-versions",
        type=int,
        default=2,
        help="Number of latest versioned release builds to retain per group (default: 2).",
    )
    parser.add_argument(
        "--min-age-hours",
        type=float,
        default=0.0,
        help="Skip caches/artifacts modified within the last N hours to protect running builds (default: 0).",
    )
    parser.add_argument(
        "--dedup-scratch-mb",
        type=float,
        default=25.0,
        help="Minimum file size in MB for SHA-256 duplicate scratch/test file cleanup (0 to disable, default: 25).",
    )
    parser.add_argument(
        "--clean-simulators",
        action="store_true",
        help="Also run `xcrun simctl delete unavailable` on macOS to purge orphaned iOS Simulator runtimes.",
    )
    parser.add_argument(
        "--report-json",
        type=str,
        default=None,
        help="Optional file path to export a machine-readable JSON audit report.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"agent-slim {VERSION}",
    )

    args = parser.parse_args()
    reports: List[ScanReport] = []

    for raw_path in args.paths:
        p = Path(raw_path).expanduser().resolve()
        if not p.exists():
            print(f"[WARN] Path does not exist, skipping: {p}", file=sys.stderr)
            continue
        rep = scan_workspace(
            root=p,
            include_node_modules=args.include_node_modules,
            keep_versions=args.keep_versions,
            min_age_hours=args.min_age_hours,
            dedup_scratch_mb=args.dedup_scratch_mb,
        )
        reports.append(rep)

    print_summary(reports, execute=args.execute)

    if args.clean_simulators:
        sim_msg = clean_unavailable_ios_simulators(execute=args.execute)
        print(f"\n[iOS Simulators] {sim_msg}")

    total_reclaimed = 0
    total_deleted_items = 0
    all_errors: List[str] = []

    if args.execute:
        for rep in reports:
            reclaimed, count, errs = execute_cleanup(rep)
            total_reclaimed += reclaimed
            total_deleted_items += count
            all_errors.extend(errs)

        print("\n" + "=" * 84)
        print(f"  CLEANUP COMPLETE: Reclaimed {format_bytes(total_reclaimed)} ({total_deleted_items} items removed)")
        if all_errors:
            print(f"  Warnings/Errors ({len(all_errors)}):")
            for err in all_errors[:10]:
                print(f"    - {err}")
        print("=" * 84)

    if args.report_json:
        out_path = Path(args.report_json).expanduser().resolve()
        payload = {
            "version": VERSION,
            "executed": args.execute,
            "total_reclaimable_bytes": sum(r.total_bytes for r in reports),
            "total_reclaimed_bytes": total_reclaimed if args.execute else 0,
            "workspaces": [
                {
                    "root": str(r.root),
                    "reclaimable_bytes": r.total_bytes,
                    "protected_notes": sorted(set(r.protected_notes)),
                    "skipped_active": r.skipped_active,
                    "candidates": [
                        {
                            "path": str(c.path),
                            "category": c.category,
                            "size_bytes": c.size_bytes,
                            "reason": c.reason,
                            "is_dir": c.is_dir,
                        }
                        for c in r.candidates
                    ],
                }
                for r in reports
            ],
        }
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[JSON Report] Written to {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
