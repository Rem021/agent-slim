# 智能体、Xcode 与多语言工作区深度瘦身工具 (`agent-slim` v2.1.0)

[![English](https://img.shields.io/badge/语言-English-0969da?style=flat)](./README.md)
[![版本](https://img.shields.io/badge/版本-v2.1.0-1a7f37?style=flat)](https://github.com/Rem021/agent-slim/releases/tag/v2.1.0)
[![系统支持](https://img.shields.io/badge/系统-苹果桌面系统_%7C_Linux-0969da?style=flat)](https://github.com/Rem021/agent-slim)
[![安全门禁](https://img.shields.io/badge/安全机制-五重硬性门禁-8250df?style=flat)](#一五阶段安全清理流水线)
[![开源协议](https://img.shields.io/badge/开源协议-MIT-656d76?style=flat)](./LICENSE)

> **语言切换**：[**👉 Switch to Pure English Documentation (`README.md`)**](./README.md)

本工具专为多智能体并行开发、Xcode/iOS/macOS 原生工程与多语言研发环境设计，采用零外部依赖架构。在不丢失任何版本控制状态、未提交代码、运行中进程上下文、被引用资源或智能体规则配置的前提下，深度清理数十至数百吉字节的编译中间产物、Xcode 系统缓存（`DerivedData`、`CoreSimulator`、`DeviceSupport`）、历史 UUID 安装事务、迭代虚拟机镜像（`.cpio`）以及导致 macOS 启动台出现禁止符号（`🚫`）的幽灵应用注册记录（`LaunchServices`）。

---

## 一、五阶段安全清理流水线

任何目录或构建产物在执行清理前，必须依次通过以下五道安全门禁校验：

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/safety-pipeline-zh-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./assets/safety-pipeline-zh-light.svg">
    <img alt="五阶段安全清理流水线" src="./assets/safety-pipeline-zh-light.svg" width="100%">
  </picture>
</p>

| 安全门禁 | 保护规则 | 校验方式 |
| :--- | :--- | :--- |
| **门禁 01** | 活跃进程与时效锁保护 | 自动扫描运行中进程命令行（`ps -axo command`）与文件修改时间窗（`--min-age-hours`），跳过正在运行的编译、虚拟机（`qemu`）或测试任务。 |
| **门禁 02** | 版本工作树保护 | 严格保护 `.git`、`.svn`、`.hg`、`.jj`、未提交修改、暂存区变更及源码文件。 |
| **门禁 03** | 智能体规则与报告保护 | 保护所有智能体配置与记忆（`CLAUDE.md`、`AGENTS.md`、`.claude/`、`.codex/`、`.orca/`）及报告文档（`.md`/`.json`/`.py`/图片），同时深入穿透 `reports/`、`outputs/`、`work/` 清理隐藏的二进制编译产物。 |
| **门禁 04** | 资源与脚本引用图校验 | 解析 `.fcpxml`、`current.json`、`.py` 与 `.sh` 脚本中的路径引用（如 `--source` 基准 `.cpio` 镜像、当前激活的 UUID 安装目录），确保被引用资源绝不误删。 |
| **门禁 05** | 多维版本与迭代产物保留 | 自动保留最新 `N` 份语义化版本包、`current.json` 指向的活跃 UUID 事务、最新迭代 `.cpio` 固件镜像及测试运行状态，仅清理被替代的历史冗余副本。 |

---

## 二、支持的开发环境与工程栈

| 类别 | 支持范围 | 清理目标 | 严格保留内容 |
| :--- | :--- | :--- | :--- |
| **智能体工作区** | Claude Code、Codex、Cursor、Windsurf、Cline、Orca、Antigravity | 散落的临时编译 `.app`、`*.saved-application`、`*.app.saved`、过期测试运行备份（`before/backup`） | 活跃会话记录、全局与项目规则文件、技能定义目录、所有 `.json`/`.manifest`/`.md` 验收回执 |
| **苹果与 Xcode 工程** | Xcode、SwiftPM、CoreSimulator、LaunchServices、Flutter、React Native | `DerivedData`、`Debug/Release-iphoneos/simulator`、`*UITests-Runner.app`、模拟器符号缓存（`coresymbolicationd`）、孤立克隆设备、`DeviceSupport`、启动台 `🚫` 幽灵应用注册（`lsregister`） | 全部源代码、`.xcodeproj`、签名证书、`/Applications` 正式应用、模拟器内活跃主应用、最新正式归档包 |
| **系统、C++ 与固件实验室** | Rust (`Cargo`)、C/C++ (`CMake`)、Go、Zig、QEMU/内核实验室 | `target/`、`cmake-build-*`、目标文件（`.o`、`.dia`、`.pch`）、历史迭代 `.cpio`/`.img`/`.fdat` 根文件系统镜像 | `Cargo.lock`、头文件目录、运行中 QEMU 挂载镜像、脚本 `--source` 引用的基准镜像 |
| **前端、Python 与影视工程** | Node (`pnpm`/`npm`/`bun`)、Next.js、Vite、Python (`uv`/`pytest`)、Final Cut Pro | `.next`、`.turbo`、`__pycache__`、`.pytest_cache`、`wandb/`、FCP 渲染缓存（`Render Files`）、SHA-256 重复临时大文件 | 依赖锁文件、`.env*`、AI 模型权重（`.safetensors`、`.gguf`、`.pt`、`.onnx`）、FCPXML 引用的原始素材 |

---

## 三、快速上手

### 1. 只读审计模式（安全预览）

对目标工作区与 Xcode 系统缓存进行全量只读扫描，仅输出可回收空间与幽灵应用统计，不删除任何文件：

```bash
python3 scripts/agent_slim.py scan --root ~/Projects --clean-xcode --clean-launchservices
```

### 2. 深度清理模式（工作区 + Xcode 缓存 + 启动台幽灵图标清理）

核对审计报告后执行永久空间回收，自动执行五道安全门禁并从 macOS LaunchServices 注销残留构建应用图标：

```bash
python3 scripts/agent_slim.py clean --root ~/Projects --keep-latest-release 2 --clean-xcode --clean-device-support --clean-orphans --clean-launchservices --shield-spotlight
```

### 3. 导出结构化报告

生成 JSON 审计报告，便于定时巡检任务或持续集成流水线调用：

```bash
python3 scripts/agent_slim.py scan --root ~/Projects --json > report.json
```

---

## 四、仓库目录结构

```text
agent-slim/
├── SKILL.md                  # 智能体技能定义与调用规范
├── scripts/
│   └── agent_slim.py         # 零依赖五重门禁扫描、清理与 Xcode/LaunchServices 优化引擎
├── assets/                   # 自适应深浅色矢量流程图
├── README.md                 # 纯英文说明文档（默认首页）
└── README.zh-CN.md           # 纯中文说明文档
```

---

## 五、开源规则引用与致谢 (Attributions & Credits)

`agent-slim` 的孤立文件检测、卸载残留识别与多语言构建清理规则参考并融合了以下优秀开源项目的核心思路由此致谢：

- **[`alienator88/Pearcleaner`](https://github.com/alienator88/Pearcleaner)**（`Locations.swift` 与 Orphan Scanner）：`~/Library` 与 `/Library` 卸载残留目录分类体系及 `LaunchAgents` 目标可执行文件校验。
- **[`tw93/Mole`](https://github.com/tw93/Mole)**（`SECURITY_AUDIT.md`、`clean_app_caches`、`clean_user_core`）：严格基于 Bundle ID 归属而非模糊名称猜测、macOS TCC / 沙盒容器（`containermanagerd` / `com.apple.provenance`）安全边界保护，以及桌面端 `*-updater` 升级暂存包清理。
- **[`momenbasel/PureMac`](https://github.com/momenbasel/PureMac)**、**[`slow-coding/fullcleaner`](https://github.com/slow-coding/fullcleaner)** 与 **[`Alyetama/Sweep`](https://github.com/Alyetama/Sweep)**：结合 `LaunchServices`（`lsregister -dump`）、`pkgutil --pkgs` 安装凭据与 10 位 Apple 开发者 `TeamID` 前缀（`<TEAMID>.<suite>`）交叉验证孤立 `Containers` 与 `Group Containers`。
- **[`jithin-sabu/purge-app`](https://github.com/jithin-sabu/purge-app)** 与 **Homebrew Cask `zap` 规则**：基于确定性二进制存在性映射清理 `Application Support`（例如按单品独立校验 Adobe 组件，清理已卸载的 `Acrobat`/`Illustrator` 残留，同时保护 `Adobe DNG Converter` 依赖的 `CameraRaw`）。
- **[`tbillington/kondo`](https://github.com/tbillington/kondo)**、**[`voidcosmos/npkill`](https://github.com/voidcosmos/npkill)**、**[`mac-cleanup/mac-cleanup-py`](https://github.com/mac-cleanup/mac-cleanup-py)** 与 **[`brege/dil`](https://github.com/brege/dil)**：在清理 `target/`、`build/`、`.build/` 等同名目录前强制校验同级工程清单锚点文件（`Cargo.toml`、`Package.swift`、`pom.xml`、`build.gradle`、`CMakeLists.txt`），以及全局包管理器缓存（`pip`、`pnpm`、`npm/_cacache`）清理规范。

---

## 六、开源协议

本项目基于 [MIT 协议](./LICENSE) 开源发布。
