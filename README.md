Python 代码异味检测插件 (Python Smell Detector)

1. 项目简介
这是一个 VS Code 扩展项目，旨在通过集成 Python 脚本（基于 Pylint）来自动检测 Python 代码中的“坏味道”（Code Smells），如长方法、重复代码等，并提供实时反馈和可视化报告。

1.1. 项目结构
team20/
    smelly_python/          (Python 后端核心逻辑)
        main.py             (分析脚本：接收文件路径，输出 JSON 格式的检测结果)
    vscode-extension/       (VS Code 插件前端代码)
        src/
            extension.ts    (插件主入口：处理事件、调用 Python、渲染红线)
        package.json        (插件配置清单)
        tsconfig.json       (TypeScript 编译配置)
    setup.py                (Python 包安装脚本)
    README.md               (项目说明文档)

2. 快速开始 (How to Run)

2.1. 环境准备 (Prerequisites)
此项目是混合开发，你需要同时安装以下环境：
2.1.1. Python 3.x: 用于运行检测算法。
2.1.2. Node.js & npm: 用于编译和运行 VS Code 插件。
推荐方式: 由于你已经安装了 Conda，直接使用 Conda 安装 Node.js 最为方便：
conda install -c conda-forge nodejs
或者下载 Node.js 官网的 Windows Installer (.msi) 版本。

2.2. 安装步骤

2.2.1. 第一步：准备 Python 端
确保你的 Python 环境正常，并且安装了 pylint。
必须安装 pylint，否则插件无法分析代码：
pip install pylint

2.2.2. 第二步：编译插件 (关键)
打开终端（Terminal），进入插件目录并安装依赖：
cd vscode-extension
npm install
npm run compile
注意：如果之前遇到 npm 报错，请重启 VS Code 后再试。

2.3. 运行与调试
2.3.1. 在 VS Code 中打开 team20/vscode-extension 文件夹。
2.3.2. 按键盘上的 F5 键。
2.3.3. 这会启动一个新的 VS Code 窗口（扩展开发宿主环境）。
2.3.4. 在新窗口中打开任意 Python 文件。
2.3.5. 测试效果 (Testing)：
打开项目根目录下的 smelly_demo.py 文件。
开始编写代码或保存文件：触发实时检测。
观察波浪线：
import json: 提示未使用的导入。
X = 1: 提示变量名不符合命名规范。
TODO: 提示需要处理的任务。
体验智能重构：
运行命令 Show Smell Report。
在报告中找到 complex_logic_demo 函数相关的警告（如 too-many-branches）。
点击右侧的 Fix It 按钮。
查看自动生成的控制流图 (CFG) 和 代码拆分建议。
2.3.6. 查看报告:
按 Ctrl+Shift+P 打开命令面板。
输入 Show Smell Report 并执行，查看报告面板。
体验新功能: 如果代码中存在复杂的函数（例如多层嵌套循环），报告中会出现 Fix It 按钮。点击它查看控制流图和重构建议。

2.4. 测试指南 (Testing Guide)
为了确保代码质量，本项目包含两套自动化测试：Python 核心逻辑测试和 VS Code 集成测试。

2.4.1. Python 核心逻辑测试 (Pytest)
测试文件位于 smelly_python/tests/test_analyzer.py，用于验证 AST 分析、CFG 生成和 Pylint 结果映射算法的正确性。
运行方法：
在项目根目录下打开终端，运行以下命令：
python -m unittest discover smelly_python/tests
或者如果您安装了 pytest：
pytest smelly_python/tests

2.4.2. VS Code 集成测试 (Mocha)
测试文件位于 vscode-extension/src/test/suite/ipc.test.ts，用于验证 TypeScript 前端与 Python 后端的 IPC 通信，确保 JSON 数据传输无误。
运行方法：
在 vscode-extension 目录下打开终端，运行以下命令：
cd vscode-extension; npm test
或者在 VS Code 中按 F5，选择 "Extension Tests" 配置进行调试运行。

2.4.3. 模糊测试 (Fuzz Testing)
为了验证分析器的健壮性，我们引入了基于变异的模糊测试。
测试文件位于 smelly_python/tests/fuzz_test.py。
该测试会生成大量随机变异的 Python 代码（包括非法语法、乱码等）输入给分析器，确保其不会因异常输入而崩溃。
运行方法：
python smelly_python/tests/fuzz_test.py

3. 功能特性 (Features)

3.1. 实时代码异味检测 (Real-time Detection)
基于 Pylint 的强大分析能力。
在编写代码时自动触发（支持防抖）。
直接在编辑器中以波浪线形式高亮显示问题（Error/Warning/Info）。
波浪线含义:
红色波浪线 (Error): 代码错误或致命问题 (对应 Pylint error, fatal)。
黄色波浪线 (Warning): 潜在的逻辑问题或坏味道 (对应 Pylint warning)。
蓝色波浪线 (Information): 编码规范建议或重构机会 (对应 Pylint convention, refactor)。

3.2. 可视化质量报告 (HTML Dashboard)
提供详细的代码质量分析报告。
包含问题统计、严重程度分类。
通过命令 Show Smell Report 一键生成。

3.3. 智能重构建议 (Smart Refactoring Suggestions) （创新点）
上下文感知: 自动识别复杂度过高（如 too-many-statements）的函数。
可视化分析: 在报告中生成函数的控制流图 (CFG)，直观展示复杂度来源。
交互式预览: 提供 Fix It 按钮，点击即可查看自动生成的重构代码预览（如 Extract Method 建议）。

4. 开发状态 (Development Status)

4.1. 核心架构: VS Code (TypeScript) + Python 混合开发架构搭建完成。
4.2. 算法集成: 已集成 Pylint，不再使用模拟数据。
4.3. 报告生成: 支持生成美观的 HTML 统计报告。
4.4. 高级错误处理: 自动检测 Python 环境路径（目前依赖系统 PATH）。

5. 常见问题
5.1. 报错 npm : 无法将“npm”项识别...: 说明你没安装 Node.js，请去官网下载安装。
5.2. 插件没反应: 确保你打开的是 Python 文件，尝试输入一些代码或按保存触发检测。

6. 项目需求与规范 (Project Requirements)

6.1. 项目核心信息
6.1.1. 非功能需求: 完成三项非功能需求，每项需搭配有合理依据的软件架构设计方案。
性能 (Performance)
体现: “实时代码异味检测 (Real-time Detection)”。
需求: 插件需要在用户输入代码时（On-Type）即时触发检测，而不仅仅是保存时。为了平衡性能，采用防抖（Debounce 500ms）机制和标准输入流（Stdin）通信，确保在不产生磁盘 I/O 的情况下，于 1 秒内返回分析结果，避免阻塞编辑器 UI。
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
可扩展性: 新增一个检测规则无需修改 extension.ts 核心代码。

6.2. 项目进度与流程
6.2.1. 开发方法: 敏捷方法 (Scrum)。
6.2.2. 冲刺周期: 至少 3 个冲刺，每周至少 1 次站会，使用燃尽图跟踪。
冲刺 1 (第 2-5 周): 用户故事、架构设计、编码、测试、评审、解决技术债务。
冲刺 2 (第 6-9 周): 包含冲刺 1 活动 + 代码质量优化。
冲刺 3 (第 10-13 周): 包含冲刺 2 活动 + 自动化测试、调试维护支持、项目收尾、展示准备。
6.2.3. 代码管理: Github 维护，记录每周活动。

6.3. 评分与交付要求
6.3.1. 展示与演示视频 (5%):
涵盖背景、动机、核心问题、相关工作、挑战解决方案、创新点、实证评估。
演示关键端到端场景、开发流程、改进点。
聚焦创新，不包含未来功能。
6.3.2. 最终报告 (20%):
核心考察: 技术创新与创造性 (A类成绩必须有创新)。
内容：报告组织、系统设计实现、测试评估、SE流程应用、自我反思、每周证据。
6.3.3. 核心模块: 需含算法、图表、代码清单、示例演示及对比评估。

6.4. 开发建议与禁忌
6.4.1. 建议:
避免从零开发全功能工具。
基于开源或插件开发，优先选择研究论文相关工具。
方向：改进现有任务、降低门槛、扩展功能、场景转换、自主创新。
6.4.2. 禁忌 (禁止开发):
电商系统
图书馆借阅系统
机器学习模型训练脚本
非软件工程工具类项目
