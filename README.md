# Python 代码异味检测插件 (Python Smell Detector)

这是一个 VS Code 扩展项目，旨在通过集成 Python 脚本（基于 Pylint）来自动检测 Python 代码中的“坏味道”（Code Smells），如长方法、重复代码等，并提供实时反馈和可视化报告。

## 📂 项目结构

```text
team20/
├── smelly_python/          # 🐍 Python 后端核心逻辑
│   └── main.py             # 分析脚本：接收文件路径，输出 JSON 格式的检测结果
├── vscode-extension/       # 🧩 VS Code 插件前端代码
│   ├── src/
│   │   └── extension.ts    # 插件主入口：处理事件、调用 Python、渲染红线
│   ├── package.json        # 插件配置清单
│   └── tsconfig.json       # TypeScript 编译配置
├── setup.py                # Python 包安装脚本
└── README.md               # 项目说明文档
```

## 🚀 快速开始 (How to Run)

### 1. 环境准备 (Prerequisites)
此项目是混合开发，你需要同时安装以下环境：
*   **Python 3.x**: 用于运行检测算法。
*   **Node.js & npm**: 用于编译和运行 VS Code 插件。
    *   **推荐方式**: 由于你已经安装了 Conda，直接使用 Conda 安装 Node.js 最为方便：
        ```bash
        conda install -c conda-forge nodejs
        ```
    *   或者下载 [Node.js 官网](https://nodejs.org/) 的 Windows Installer (.msi) 版本。

### 2. 安装步骤

#### 第一步：准备 Python 端
确保你的 Python 环境正常，并且安装了 `pylint`。
```bash
# 必须安装 pylint，否则插件无法分析代码
pip install pylint
```

#### 第二步：编译插件 (关键)
打开终端（Terminal），进入插件目录并安装依赖：

```bash
cd vscode-extension
npm install
npm run compile
```
*注意：如果之前遇到 npm 报错，请重启 VS Code 后再试。*

### 3. 运行与调试
1.  在 VS Code 中打开 `team20/vscode-extension` 文件夹。
2.  按键盘上的 **F5** 键。
3.  这会启动一个新的 VS Code 窗口（扩展开发宿主环境）。
4.  在新窗口中打开任意 Python 文件。
5.  **测试效果 (Testing)**：
    *   打开项目根目录下的 `smelly_demo.py` 文件。
    *   **保存文件 (Ctrl+S)**：触发实时检测。
    *   **观察波浪线**：
        *   `import json`: 提示未使用的导入。
        *   `X = 1`: 提示变量名不符合命名规范。
        *   `TODO`: 提示需要处理的任务。
    *   **体验智能重构**：
        *   运行命令 `Show Smell Report`。
        *   在报告中找到 `complex_logic_demo` 函数相关的警告（如 `too-many-branches`）。
        *   点击右侧的 **"Fix It 🔧"** 按钮。
        *   查看自动生成的**控制流图 (CFG)** 和 **代码拆分建议**。

更新 smelly_demo.py：
重写了测试文件，现在包含多种类型的“代码异味”：
基础异味：未使用的导入 (import json)、不规范命名 (X = 1)、TODO 注释。
复杂性异味：complex_logic_demo 函数包含多层嵌套的 if/elif 和 for 循环，旨在触发 too-many-branches 或 too-many-statements 警告，从而激活新的“智能重构建议”功能。
重复代码：两个完全相同的函数块，用于测试重复代码检测。

6.  **查看报告**:
    *   按 `Ctrl+Shift+P` 打开命令面板。
    *   输入 `Show Smell Report` 并执行，查看报告面板。
    *   **体验新功能**: 如果代码中存在复杂的函数（例如多层嵌套循环），报告中会出现 **"Fix It 🔧"** 按钮。点击它查看控制流图和重构建议。

## ☁️ 云端与 CI/CD 集成 (Cloud & CI/CD Integration)

本项目支持在 GitHub 平台上直接运行，提供两种集成方式：

### 方式一：GitHub Codespaces (推荐)
在浏览器中获得完整的 VS Code 开发体验，无需本地配置环境。

1.  在 GitHub 仓库页面，点击绿色的 **Code** 按钮。
2.  切换到 **Codespaces** 标签页，点击 **Create codespace on main**。
3.  等待环境初始化（会自动安装 Python, Node.js, Pylint 等依赖）。
4.  按 **F5** 启动调试，即可在云端体验插件功能。

### 方式二：GitHub Actions (自动检测)
每次提交代码时自动运行代码异味检测，无需人工干预。

*   配置文件位于 `.github/workflows/smell-check.yml`。
*   **触发机制**: 当代码 Push 到仓库或提交 Pull Request 时自动触发。
*   **查看结果**: 在 GitHub 仓库的 **Actions** 标签页查看检测日志。

## ✨ 功能特性 (Features)

1.  **实时代码异味检测 (Real-time Detection)**:
    *   基于 **Pylint** 的强大分析能力。
    *   在保存文件时自动触发。
    *   直接在编辑器中以波浪线形式高亮显示问题（Error/Warning/Info）。
    *   **波浪线含义**:
        *   🔴 **红色波浪线 (Error)**: 代码错误或致命问题 (对应 Pylint `error`, `fatal`)。
        *   🟡 **黄色波浪线 (Warning)**: 潜在的逻辑问题或坏味道 (对应 Pylint `warning`)。
        *   🔵 **蓝色波浪线 (Information)**: 编码规范建议或重构机会 (对应 Pylint `convention`, `refactor`)。

2.  **可视化质量报告 (HTML Dashboard)**:
    *   提供详细的代码质量分析报告。
    *   包含问题统计、严重程度分类。
    *   通过命令 `Show Smell Report` 一键生成。

3.  **智能重构建议 (Smart Refactoring Suggestions) （创新点）**:
    *   **上下文感知**: 自动识别复杂度过高（如 `too-many-statements`）的函数。
    *   **可视化分析**: 在报告中生成函数的**控制流图 (CFG)**，直观展示复杂度来源。
    *   **交互式预览**: 提供 **"Fix It 🔧"** 按钮，点击即可查看自动生成的**重构代码预览**（如 Extract Method 建议）。

## 🛠️ 开发状态 (Development Status)

- [x] **核心架构**: VS Code (TypeScript) + Python 混合开发架构搭建完成。
- [x] **算法集成**: 已集成 Pylint，不再使用模拟数据。
- [x] **报告生成**: 支持生成美观的 HTML 统计报告。
- [ ] **高级错误处理**: 自动检测 Python 环境路径（目前依赖系统 PATH）。

## 常见问题
*   **报错 `npm : 无法将“npm”项识别...`**: 说明你没安装 Node.js，请去官网下载安装。
*   **插件没反应**: 确保你打开的是 Python 文件，并且按了保存（Ctrl+S）触发检测。

## 📋 项目需求与规范 (Project Requirements)

### 一、项目核心信息
*   **非功能需求**: 完成三项非功能需求，每项需搭配有合理依据的软件架构设计方案。
性能 (Performance)
体现: “实时代码异味检测 (Real-time Detection)”。
需求: 插件需要在用户保存文件后的极短时间内（例如 < 1秒）完成 Python 脚本调用、分析并返回结果，以免阻塞编辑器 UI 或影响开发体验。
可用性 (Usability)
体现: “可视化质量报告 (Visual Quality Report)” 和 “波浪线警告”。
需求: 必须提供直观的用户界面（HTML 仪表盘、编辑器内联高亮），降低用户理解代码问题的门槛，无需离开 IDE 即可获取反馈。
可维护性/可扩展性 (Maintainability/Extensibility)
体现: 采用 TypeScript (前端) + Python (后端) 的分离架构。
需求: 这种架构设计允许独立更新检测算法（Python 端）而无需修改插件逻辑（TS 端），或者方便地添加新的“异味”检测规则（基于 Pylint 扩展）。
建议：
为了满足“搭配有合理依据的软件架构设计方案”这一要求，建议在后续文档中明确量化这三点，例如：

性能: 分析 1000 行代码的时间不超过 2 秒。
可用性: 报告生成需在 3 步操作内完成。
3可扩展性: 新增一个检测规则无需修改 extension.ts 核心代码。 

### 二、项目进度与流程
*   **开发方法**: 敏捷方法 (Scrum)。
*   **冲刺周期**: 至少 3 个冲刺，每周至少 1 次站会，使用燃尽图跟踪。
    *   **冲刺 1 (第 2-5 周)**: 用户故事、架构设计、编码、测试、评审、解决技术债务。
    *   **冲刺 2 (第 6-9 周)**: 包含冲刺 1 活动 + 代码质量优化。
    *   **冲刺 3 (第 10-13 周)**: 包含冲刺 2 活动 + 自动化测试、调试维护支持、项目收尾、展示准备。
*   **代码管理**: Github 维护，记录每周活动。

### 三、评分与交付要求
*   **展示与演示视频 (5%)**:
    *   涵盖背景、动机、核心问题、相关工作、挑战解决方案、创新点、实证评估。
    *   演示关键端到端场景、开发流程、改进点。
    *   聚焦创新，不包含未来功能。
*   **最终报告 (20%)**:
    *   **核心考察**: 技术创新与创造性 (A类成绩必须有创新)。
    *   内容：报告组织、系统设计实现、测试评估、SE流程应用、自我反思、每周证据。
*   **核心模块**: 需含算法、图表、代码清单、示例演示及对比评估。

### 四、开发建议与禁忌
*   **建议**:
    *   避免从零开发全功能工具。
    *   基于开源或插件开发，优先选择研究论文相关工具。
    *   方向：改进现有任务、降低门槛、扩展功能、场景转换、自主创新。
*   **禁忌 (禁止开发)**:
    *   电商系统
    *   图书馆借阅系统
    *   机器学习模型训练脚本
    *   非软件工程工具类项目
