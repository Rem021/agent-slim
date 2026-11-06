# 智能体与多语言工作区深度瘦身工具

[![English](https://img.shields.io/badge/语言-English-0969da?style=flat)](./README.md)
[![版本](https://img.shields.io/badge/版本-v2.0.0-1a7f37?style=flat)](https://github.com/Rem021/agent-slim/releases/tag/v2.0.0)
[![系统支持](https://img.shields.io/badge/系统-苹果桌面系统_%7C_Linux-0969da?style=flat)](https://github.com/Rem021/agent-slim)
[![安全门禁](https://img.shields.io/badge/安全机制-五重硬性门禁-8250df?style=flat)](#一五阶段安全清理流水线)
[![开源协议](https://img.shields.io/badge/开源协议-MIT-656d76?style=flat)](./LICENSE)

> **语言切换**：[**👉 Switch to Pure English Documentation (`README.md`)**](./README.md)

本工具专为多智能体并行开发与多语言工程环境设计，采用零外部依赖架构。在不丢失任何版本控制状态、未提交代码、活跃任务上下文、被引用资源或智能体规则配置的前提下，安全清理数十吉字节的编译中间产物、过期日志与历史构建包。

---

## 一、五阶段安全清理流水线

任何目录在执行清理前，必须依次通过以下五道安全门禁校验：

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/safety-pipeline-zh-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./assets/safety-pipeline-zh-light.svg">
    <img alt="五阶段安全清理流水线" src="./assets/safety-pipeline-zh-light.svg" width="100%">
  </picture>
</p>

| 安全门禁 | 保护规则 | 校验方式 |
| :--- | :--- | :--- |
| **门禁 01** | 活跃进程锁保护 | 自动检测并跳过存在运行中编译、测试或被进程占用句柄的工作区目录。 |
| **门禁 02** | 版本工作树保护 | 严格保护未提交修改、暂存区变更、未跟踪源码文件以及暂存栈内容。 |
| **门禁 03** | 智能体会话保护 | 保留所有活跃任务列表、工作区规则文档以及处于保护时间窗内的会话上下文。 |
| **门禁 04** | 资源引用图校验 | 扫描源码与文档引用关系，确保被引用的图片、模型权重与测试样本绝不误删。 |
| **门禁 05** | 最新构建包保留 | 每个工程自动保留最新一份可运行构建产物，仅清理历史冗余归档包。 |

---

## 二、支持的开发环境与工程栈

| 类别 | 支持范围 | 清理目标 | 严格保留内容 |
| :--- | :--- | :--- | :--- |
| **智能体工作区** | 主流命令行与桌面编程智能体工作树 | 过期调试日志、孤立浏览器缓存、废弃工作树构建目录 | 活跃会话记录、全局与项目规则文件、技能定义目录 |
| **苹果与移动端工程** | 原生桌面与移动端编译环境及跨平台框架 | 派生编译缓存、中间符号表、旧版历史归档包 | 全部源代码、工程配置文件、签名证书、最新可运行包 |
| **系统与原生编译栈** | 系统级编译语言与跨平台构建工具链 | 调试构建目录、中间目标文件、着色器编译缓存 | 依赖锁文件、头文件目录、第三方预编译静态库 |
| **前端与脚本工程** | 现代前端打包框架与脚本语言虚拟环境 | 打包工具缓存、字节码缓存、单元测试与类型检查缓存 | 依赖锁文件、环境变量配置、本地数据库文件、活跃虚拟环境 |

---

## 三、快速上手

### 1. 只读审计模式（安全预览）

对目标工作区进行全量只读扫描，仅输出可回收空间报告，不修改或删除任何文件：

```bash
python3 scripts/agent_slim.py scan --root ~/Projects
```

### 2. 安全清理模式

核对审计报告后执行安全清理（全程自动强制执行五道安全门禁）：

```bash
python3 scripts/agent_slim.py clean --root ~/Projects --keep-latest-release 1
```

### 3. 导出结构化报告

生成结构化数据文件，便于定时巡检任务或持续集成流水线调用：

```bash
python3 scripts/agent_slim.py scan --root ~/Projects --json > report.json
```

---

## 四、仓库目录结构

```text
agent-slim/
├── SKILL.md                  # 智能体技能定义与调用规范
├── scripts/
│   └── agent_slim.py         # 零依赖五重门禁扫描与清理主程序
├── assets/                   # 自适应深浅色矢量流程图
├── README.md                 # 纯英文说明文档（默认首页）
└── README.zh-CN.md           # 纯中文说明文档
```

---

## 五、开源协议

本项目基于 [MIT 协议](./LICENSE) 开源发布。
