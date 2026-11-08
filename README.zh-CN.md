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
python3 scripts/agent_slim.py clean --root ~/Projects --keep-latest-release 2 --clean-xcode --clean-device-support --clean-launchservices --shield-spotlight
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

## 五、开源协议

本项目基于 [MIT 协议](./LICENSE) 开源发布。
