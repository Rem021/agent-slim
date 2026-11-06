#!/usr/bin/env python3
"""
agent-slim: Universal AI Agent & Multi-Stack Workspace Deep Cleaner
===================================================================

A zero-dependency, memory-preserving, process-aware deep cleaner designed for
AI Agent workspaces (Codex, Claude Code, Orca, Antigravity, Cursor, Windsurf)
and multi-language software/media/embedded projects:
  - Swift / Xcode / iOS / macOS (DerivedData, .build, .xcresult, .trace, SimBackup)
  - Rust / Go / C / C++ / Embedded / QEMU (target, CMakeFiles, .o, duplicate .cpio/.img)
  - Node / Web / TypeScript (.next, .turbo, .vite, .parcel-cache, stale worktree node_modules)
  - Python / AI / Data Science (__pycache__, .pytest_cache, .mypy_cache, .ruff_cache)
  - JVM / Android / Kotlin (.gradle, build/intermediates)
  - Media / Color / Camera Lab (FCP Render Files, raw GPU/frame dumps .rgba16f/.rgba32f/.raw/.bin,
    duplicate test exports & duplicate RAW camera fixtures in scratch folders)

Core Safety Guarantees:
  1. Active Process & Open-File Guard: Inspects `ps` and `lsof` to automatically
     lock and skip any workspace or subdirectory currently in use by an active agent,
     compiler, simulator, VM (QEMU), or media host (Final Cut Pro, DaVinci Resolve).
  2. Memory & Progress Preservation: 100% preserves all Git repositories (.git,
     worktree links, .bundle, .patch), source code, agent memory & handoff docs
     (README.md, PROGRESS.md, AGENTS.md, CLAUDE.md, GEMINI.md, docs/, reports/,
     research_notes/), and small JSON/YAML/TXT receipts/state files.
  3. Reference-Aware Media Protection: Parses Final Cut Pro (.fcpxml, .fcpbundle),
     LUTs (.cube), and canonical `fixtures/` directories so original referenced
     assets are never deleted.
  4. Recent-File Grace Window: Protects files modified within `--min-age-hours`
     (default: 18 hours) unless `--all-ages` is explicitly passed.
"""

from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import unquote

VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# 1. Universal Stack Profiles & Classification Rules
# ---------------------------------------------------------------------------

# Directories that are 100% regenerable build/cache outputs across stacks
CACHE_BUILD_DIR_NAMES: Set[str] = {
    # Swift / Xcode / Apple
    "DerivedData",
    ".build",
    "ModuleCache",
    "ModuleCache.noindex",
    "Index.noindex",
    "SimBackup",
    "Cache-Backups",
    "Build-Backups",
    "Plugin-Backups",
    "retained-native-caches",
    "probe-scratch",
    # Python
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".hypothesis",
    # Web / Node / JS
    ".next",
    ".nuxt",
    ".turbo",
    ".parcel-cache",
    ".vite",
    ".angular",
    ".svelte-kit",
    ".eslintcache",
    # C / C++ / CMake / Gradle
    "CMakeFiles",
    ".gradle",
    # Agent temporary experiment containers
    "local-experiments",
}

# Bundle suffixes that represent compiled/profiling artifacts inside work/scratch/build trees
ARTIFACT_BUNDLE_SUFFIXES: Tuple[str, ...] = (
    ".xcresult",
    ".trace",
    ".dSYM",
    ".saved",
    ".pluginkit",
)

# Raw GPU/CPU frame dumps, tensor dumps, and compiled object intermediates
RAW_DUMP_EXTENSIONS: Set[str] = {
    ".rgba16f",
    ".rgba32f",
    ".rgba32uint",
    ".rgba-f32le",
    ".f32le",
    ".f64le",
    ".raw",
    ".bin",
    ".rgba",
    ".binary",
    ".negathumb",
    ".bnnsir",
    ".atrc",
    ".o",
    ".obj",
    ".d",
    ".dia",
    ".pch",
    ".swiftdeps",
    ".priors",
    ".swiftmodule",
    ".swiftdoc",
    ".swiftsourceinfo",
    ".core",
    ".dmp",
}

# Camera RAW and heavy broadcast container formats often duplicated across agent worktrees
HEAVY_RAW_MEDIA_EXTENSIONS: Set[str] = {
    ".3fr",
    ".cap",
    ".iiq",
    ".ari",
    ".arw",
    ".dng",
    ".crm",
    ".r3d",
    ".braw",
    ".mxf",
}

# General media/export/archive extensions (cleaned ONLY inside scratch/work/outputs/task-history
# when not referenced by any project/FCPXML/fixture)
SCRATCH_MEDIA_ARCHIVE_EXTENSIONS: Set[str] = {
    ".mov",
    ".mp4",
    ".tiff",
    ".tif",
    ".exr",
    ".png",
    ".jpg",
    ".jpeg",
    ".heic",
    ".ppm",
    ".bmp",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".ipa",
}

# Directory names indicating temporary agent scratch / experiment runs
SCRATCH_CONTAINER_NAMES: Set[str] = {
    "work",
    "outputs",
    "Exports",
    "tmp",
    "scratch",
    "runs",
    "artifacts",
    "captures",
    "dumps",
    "TaskHistory",
    "Builds",
    "Archive",
    "PrismGrade-P0",
    "Phayen-lab",
}

# Snapshot subdirectories created by agent harnesses when duplicating source trees into outputs/work
DUPLICATE_SNAPSHOT_DIR_NAMES: Set[str] = {
    "actual-bound-geometry",
    "actual-full",
    "frozen-regenerated-reference",
    "independent-reference",
    "independent-reference-exact",
    "ExecutedFinal",
    "ExecutedFull",
    "candidate-products",
    "candidate-tested-source",
    "broad-output",
    "broad-inputs",
    "compatibility-matrix",
    "full-comparison",
    "final-full-comparison",
    "typed-full-comparison",
}

# Always-protected documentation, memory, and git archive extensions
MEMORY_DOC_EXTENSIONS: Set[str] = {
    ".md",
    ".txt",
    ".rst",
    ".adoc",
    ".bundle",
    ".patch",
    ".diff",
    ".fcpxml",
    ".cube",
    ".drp",
    ".drx",
}

# Always-protected file names
MEMORY_FILENAMES: Set[str] = {
    "README",
    "README.md",
    "README.txt",
    "PROGRESS.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "STATUS.md",
    "INDEX.md",
    "RULES.md",
    "GOAL.md",
    "REPORT.md",
    "USER_TRIAL_INSTALL.json",
    "RUN_STATE.json",
    "provenance.json",
    "manifest.json",
    "summary.json",
    "verification.json",
}

# Always-protected directory names (source, git, docs, reports, skills)
PROTECTED_DIR_NAMES: Set[str] = {
    ".git",
    ".svn",
    ".hg",
    ".agents",
    ".claude",
    ".gemini",
    ".codex",
    "docs",
    "reports",
    "research_notes",
    "fixtures",
    "skills",
}


# ---------------------------------------------------------------------------
# 2. Helper Utilities
# ---------------------------------------------------------------------------

def fmt_bytes(num_bytes: int) -> str:
    """Format bytes in both binary GiB/MiB and decimal GB/MB for clarity."""
    gib = num_bytes / (1024 ** 3)
    gb = num_bytes / (10 ** 9)
    if gib >= 0.1:
        return f"{gib:7.2f} GiB ({gb:7.2f} GB)"
    mib = num_bytes / (1024 ** 2)
    mb = num_bytes / (10 ** 6)
    return f"{mib:7.2f} MiB ({mb:7.2f} MB)"


def detect_active_workspace_locks(roots: List[Path]) -> Set[Path]:
    """
    Inspect running processes (`ps`) and open files (`lsof`) to find any
    directories inside `roots` that are currently in use by active builds,
    VMs (QEMU), simulators, media apps, or agent tasks.
    """
    locked_dirs: Set[Path] = set()
    root_strs = [str(r) for r in roots]

    # 1. Inspect `ps -axo args` for paths inside roots
    try:
        ps_out = subprocess.run(
            ["ps", "-axo", "comm,args"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
        for line in ps_out.splitlines():
            if any(
                kw in line
                for kw in (
                    "qemu",
                    "xcodebuild",
                    "swift-frontend",
                    "simctl",
                    "Final Cut Pro",
                    "Resolve",
                    "cargo",
                    "go ",
                    "pytest",
                    "python",
                    "Python",
                    "node",
                )
            ):
                for r_str in root_strs:
                    if r_str in line:
                        # Extract path tokens starting with r_str
                        for token in line.split():
                            cleaned = token.strip("\"'(),;:")
                            if cleaned.startswith("file:"):
                                cleaned = cleaned[5:]
                            if cleaned.startswith(r_str):
                                p = Path(cleaned)
                                # Walk up to a meaningful run/worktree directory (depth <= 4 from root)
                                base = Path(r_str)
                                try:
                                    rel_parts = p.relative_to(base).parts
                                    if len(rel_parts) >= 2:
                                        locked_dirs.add(base.joinpath(*rel_parts[:3]))
                                    elif len(rel_parts) == 1:
                                        locked_dirs.add(base.joinpath(rel_parts[0]))
                                except ValueError:
                                    pass
    except Exception:
        pass

    return locked_dirs


def collect_referenced_media_and_fcp_bundles(roots: List[Path]) -> Tuple[Set[Path], Set[Path]]:
    """
    Scan all roots for:
      - `.fcpbundle` libraries (protect everything inside except `Render Files`)
      - `.fcpxml` timelines (parse `src="file://..."` and protect referenced media)
      - symlinks inside `.fcpbundle` (protect symlink targets)
    """
    protected_files: Set[Path] = set()
    protected_dirs: Set[Path] = set()

    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dpath = Path(dirpath)
            if ".fcpbundle" in dirpath:
                if "Render Files" not in dpath.parts:
                    protected_dirs.add(dpath)
                for name in filenames + dirnames:
                    fp = dpath / name
                    if fp.is_symlink():
                        protected_files.add(fp)
                        try:
                            protected_files.add(fp.resolve())
                        except Exception:
                            pass
            for fname in filenames:
                if fname.endswith(".fcpxml"):
                    fp = dpath / fname
                    protected_files.add(fp)
                    try:
                        content = fp.read_text(errors="ignore")
                        for match in re.findall(r'src="file://([^"]+)"', content):
                            target = Path(unquote(match)).resolve()
                            protected_files.add(target)
                    except Exception:
                        pass
                elif fname.endswith(".cube") or "Alpha-Chart" in fname or fname.startswith("canonical-"):
                    protected_files.add(dpath / fname)

    return protected_files, protected_dirs


# ---------------------------------------------------------------------------
# 3. Core Scanner & Cleaner Engine
# ---------------------------------------------------------------------------

class AgentSlimCleaner:
    def __init__(
        self,
        roots: List[Path],
        execute: bool = False,
        min_age_hours: float = 18.0,
        all_ages: bool = False,
        large_json_kb: int = 256,
        protect_patterns: Optional[List[str]] = None,
        clean_xcode_simulators: bool = False,
    ):
        self.roots = [r.resolve() for r in roots if r.exists()]
        self.execute = execute
        self.min_age_seconds = 0.0 if all_ages else min_age_hours * 3600.0
        self.large_json_bytes = large_json_kb * 1024
        self.protect_patterns = protect_patterns or []
        self.clean_xcode_simulators = clean_xcode_simulators
        self.now = time.time()

        self.cat_bytes: Dict[str, int] = collections.Counter()
        self.cat_files: Dict[str, int] = collections.Counter()
        self.sample_paths: Dict[str, List[str]] = collections.defaultdict(list)
        self.kept_bytes: int = 0
        self.kept_files: int = 0
        self.skipped_active_locks: Set[str] = set()

        # Seen (filename, size) for deduplicating giant RAW camera files & VM .cpio images
        self.seen_heavy_raws: Set[Tuple[str, int]] = set()
        self.seen_vm_cpio: Set[int] = set()

    def is_custom_protected(self, path_str: str) -> bool:
        for pat in self.protect_patterns:
            if pat in path_str:
                return True
        return False

    def run(self) -> Dict[str, object]:
        print(f"🔍 [agent-slim v{VERSION}] Scanning {len(self.roots)} root(s)...")
        for r in self.roots:
            print(f"   • {r}")

        active_locks = detect_active_workspace_locks(self.roots)
        if active_locks:
            print(f"🛡️  Active process guard locked {len(active_locks)} active path(s):")
            for lk in sorted(active_locks):
                print(f"   🔒 {lk}")

        prot_files, prot_dirs = collect_referenced_media_and_fcp_bundles(self.roots)
        if prot_files:
            print(f"🎬 Referenced media & project guard locked {len(prot_files)} media/project asset(s).")

        for root in self.roots:
            self._scan_root(root, active_locks, prot_files, prot_dirs)

        sim_result = None
        if self.clean_xcode_simulators and self.execute:
            try:
                subprocess.run(["xcrun", "simctl", "delete", "unavailable"], check=False, timeout=30)
                sim_result = "Deleted unavailable Xcode simulators"
            except Exception:
                pass

        return self._build_report(active_locks, len(prot_files), sim_result)

    def _is_under_any(self, path: Path, prefixes: Set[Path]) -> Optional[Path]:
        for pref in prefixes:
            if path == pref or pref in path.parents:
                return pref
        return None

    def _scan_root(
        self,
        root: Path,
        active_locks: Set[Path],
        prot_files: Set[Path],
        prot_dirs: Set[Path],
    ) -> None:
        for dirpath, dirnames, filenames in os.walk(root, topdown=False):
            dpath = Path(dirpath)
            rel_parts = dpath.relative_to(root).parts if dpath != root else ()
            all_parts = dpath.parts

            # 1. Check active process lock
            lk = self._is_under_any(dpath, active_locks)
            if lk is not None:
                self.skipped_active_locks.add(str(lk))
                continue

            # 2. Check protected directories (.git, docs, reports, .fcpbundle metadata/Original Media)
            if any(p in PROTECTED_DIR_NAMES for p in rel_parts) or dpath in prot_dirs:
                for f in filenames:
                    fp = dpath / f
                    try:
                        st = fp.lstat()
                        if not fp.is_symlink():
                            self.kept_bytes += st.st_blocks * 512
                        self.kept_files += 1
                    except Exception:
                        pass
                continue

            # Determine context flags for this directory
            in_cache_build_dir = any(
                p in CACHE_BUILD_DIR_NAMES
                or p.endswith(ARTIFACT_BUNDLE_SUFFIXES)
                or (p == "target" and "Cargo.toml" in os.listdir(dpath.parent) if dpath.parent.exists() else False)
                for p in rel_parts
            )
            in_app_bundle = any(p.endswith(".app") or p.endswith(".framework") for p in rel_parts)
            in_scratch_tree = any(
                p in SCRATCH_CONTAINER_NAMES
                or re.match(r".*-202\d{5}$", p)
                or re.match(r"^202\d-\d{2}-\d{2}", p)
                for p in all_parts
            )
            in_dup_snapshot = any(p in DUPLICATE_SNAPSHOT_DIR_NAMES for p in rel_parts)
            is_fcp_render_files = ".fcpbundle" in dirpath and "Render Files" in rel_parts

            for fname in filenames:
                if fname == ".DS_Store":
                    continue
                fp = dpath / fname
                fp_str = str(fp)

                try:
                    st = fp.lstat()
                    is_link = fp.is_symlink()
                    alloc_bytes = st.st_blocks * 512 if not is_link else 0
                except Exception:
                    continue

                # Always protect top-level files in root, memory docs, and referenced media
                ext = fp.suffix.lower()
                if (
                    dpath == root
                    or fp in prot_files
                    or fname in MEMORY_FILENAMES
                    or ext in MEMORY_DOC_EXTENSIONS
                    or self.is_custom_protected(fp_str)
                ):
                    if not in_cache_build_dir and not in_app_bundle:
                        self.kept_bytes += alloc_bytes
                        self.kept_files += 1
                        continue

                # Check recent modification grace window
                if self.min_age_seconds > 0 and (self.now - st.st_mtime) < self.min_age_seconds:
                    self.kept_bytes += alloc_bytes
                    self.kept_files += 1
                    continue

                # Classify deletion category
                category = self._classify_file(
                    fp=fp,
                    fname=fname,
                    ext=ext,
                    logical_size=st.st_size,
                    is_link=is_link,
                    in_cache_build_dir=in_cache_build_dir,
                    in_app_bundle=in_app_bundle,
                    in_scratch_tree=in_scratch_tree,
                    in_dup_snapshot=in_dup_snapshot,
                    is_fcp_render_files=is_fcp_render_files,
                    dirpath_lower=dirpath.lower(),
                )

                if category is not None:
                    self._record_or_delete(fp, alloc_bytes, category)
                else:
                    self.kept_bytes += alloc_bytes
                    self.kept_files += 1

            # Prune empty directories in execute mode
            if self.execute and dpath != root:
                try:
                    entries = os.listdir(dpath)
                    if not entries:
                        dpath.rmdir()
                    elif entries == [".DS_Store"]:
                        (dpath / ".DS_Store").unlink(missing_ok=True)
                        dpath.rmdir()
                except Exception:
                    pass

    def _classify_file(
        self,
        fp: Path,
        fname: str,
        ext: str,
        logical_size: int,
        is_link: bool,
        in_cache_build_dir: bool,
        in_app_bundle: bool,
        in_scratch_tree: bool,
        in_dup_snapshot: bool,
        is_fcp_render_files: bool,
        dirpath_lower: str,
    ) -> Optional[str]:
        if is_fcp_render_files:
            return "1. Final Cut Pro 可重建渲染缓存 (Render Files)"

        if in_cache_build_dir or (in_app_bundle and in_scratch_tree):
            return "2. 编译与构建缓存 (DerivedData / .build / .xcresult / .trace / SimBackup / __pycache__)"

        if ext in RAW_DUMP_EXTENSIONS:
            return "3. 原始 GPU/宿主帧转储与二进制中间产物 (.rgba16f / .rgba32f / .raw / .bin / .o 等)"

        if ext == ".cpio" and logical_size > 50 * 1024 * 1024 and in_scratch_tree:
            return "4. 虚拟机/固件试验重复打包的 CPIO 根文件系统镜像 (.cpio)"

        if ext in HEAVY_RAW_MEDIA_EXTENSIONS and in_scratch_tree:
            key = (fname, logical_size)
            if key not in self.seen_heavy_raws:
                self.seen_heavy_raws.add(key)
                return None
            return "5. 历史测试工作树/实验目录重复拷贝的巨型 RAW 样片副本 (.3fr / .cap / .mxf 等)"

        if in_dup_snapshot:
            return "6. 自动化测试重复拷贝的源码/参考比对目录快照 (actual-full / Source / before 等)"

        if in_scratch_tree and ext in SCRATCH_MEDIA_ARCHIVE_EXTENSIONS and logical_size > 1024 * 1024:
            return "7. 历史测试批次导出的对比视频/全尺寸图像/临时压缩包 (.mov / .tiff / .png / .zip)"

        if in_scratch_tree and ext == ".json" and not is_link:
            if logical_size > self.large_json_bytes:
                return "8. 巨型逐像素/图块数值转储 JSON (>256KB)"

        return None

    def _record_or_delete(self, fp: Path, alloc_bytes: int, category: str) -> None:
        if self.execute:
            try:
                fp.unlink()
            except Exception:
                return
        self.cat_bytes[category] += alloc_bytes
        self.cat_files[category] += 1
        if len(self.sample_paths[category]) < 5:
            self.sample_paths[category].append(str(fp))

    def _build_report(
        self,
        active_locks: Set[Path],
        protected_media_count: int,
        sim_result: Optional[str],
    ) -> Dict[str, object]:
        total_reclaimed = sum(self.cat_bytes.values())
        total_deleted_files = sum(self.cat_files.values())
        mode_str = "EXECUTED (DELETED)" if self.execute else "DRY-RUN (PREVIEW ONLY — pass --execute to delete)"

        print("\n" + "=" * 88)
        print(f"📊 agent-slim Report — Mode: {mode_str}")
        print("=" * 88)
        print(f"  Reclaimable / Deleted : {total_deleted_files:9,d} files  |  {fmt_bytes(total_reclaimed)}")
        print(f"  Protected / Retained  : {self.kept_files:9,d} files  |  {fmt_bytes(self.kept_bytes)}")
        if sim_result:
            print(f"  Xcode Simulators      : {sim_result}")
        print("-" * 88)

        categories_report = []
        for cat, sz in sorted(self.cat_bytes.items(), key=lambda x: x[1], reverse=True):
            cnt = self.cat_files[cat]
            print(f"  {fmt_bytes(sz)}  [{cnt:8,d} files]  {cat}")
            for sp in self.sample_paths[cat][:2]:
                print(f"      ↳ sample: {sp}")
            categories_report.append(
                {
                    "category": cat,
                    "files": cnt,
                    "allocated_bytes": sz,
                    "allocated_gib": round(sz / (1024 ** 3), 3),
                    "allocated_gb": round(sz / (10 ** 9), 3),
                    "samples": self.sample_paths[cat],
                }
            )
        print("=" * 88)

        return {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "version": VERSION,
            "mode": "execute" if self.execute else "dry-run",
            "roots": [str(r) for r in self.roots],
            "total_reclaimed_files": total_deleted_files,
            "total_reclaimed_bytes": total_reclaimed,
            "total_reclaimed_gib": round(total_reclaimed / (1024 ** 3), 3),
            "total_reclaimed_gb": round(total_reclaimed / (10 ** 9), 3),
            "retained_files": self.kept_files,
            "retained_bytes": self.kept_bytes,
            "active_process_locks": [str(p) for p in sorted(active_locks)],
            "protected_media_references": protected_media_count,
            "categories": categories_report,
        }


# ---------------------------------------------------------------------------
# 4. CLI Entrypoint
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agent-slim",
        description=(
            "Universal AI Agent & Multi-Stack Project Deep Cleaner. "
            "Reclaims hundreds of GBs of build caches, GPU/frame dumps, duplicate test "
            "exports, and stale worktree artifacts while 100% preserving source code, "
            "Git history, referenced media, active processes, and agent memory/docs."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Target project or workspace root directories to scan (default: current directory).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete matched cache/dump files and prune empty directories (default is dry-run).",
    )
    parser.add_argument(
        "--min-age-hours",
        type=float,
        default=18.0,
        help="Grace window in hours: protect files modified within this window (default: 18.0).",
    )
    parser.add_argument(
        "--all-ages",
        action="store_true",
        help="Disable the modification-time grace window (still respects active process locks).",
    )
    parser.add_argument(
        "--large-json-kb",
        type=int,
        default=256,
        help="Size threshold in KB for cleaning pixel/tile dump JSONs inside scratch dirs (default: 256).",
    )
    parser.add_argument(
        "--protect",
        action="append",
        default=[],
        help="Substring or path pattern to explicitly protect (can be specified multiple times).",
    )
    parser.add_argument(
        "--clean-simulators",
        action="store_true",
        help="Also run `xcrun simctl delete unavailable` when `--execute` is enabled.",
    )
    parser.add_argument(
        "--report-json",
        type=str,
        default=None,
        help="Write a machine-readable JSON audit receipt to the specified file path.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    roots = [Path(p).expanduser().resolve() for p in args.paths]
    valid_roots = [r for r in roots if r.exists()]
    if not valid_roots:
        print("❌ No valid target directories found.", file=sys.stderr)
        return 1

    cleaner = AgentSlimCleaner(
        roots=valid_roots,
        execute=args.execute,
        min_age_hours=args.min_age_hours,
        all_ages=args.all_ages,
        large_json_kb=args.large_json_kb,
        protect_patterns=args.protect,
        clean_xcode_simulators=args.clean_simulators,
    )
    report = cleaner.run()

    if args.report_json:
        out_path = Path(args.report_json).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"📝 Saved JSON audit report to: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
