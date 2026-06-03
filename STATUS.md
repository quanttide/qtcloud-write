# STATUS

## examples/ — 各子项目概括

| 子目录 | 思路概括 | 技术栈 |
|--------|---------|--------|
| **p01-writing-poc** | 3R 方法论（Review → Reflect → Rewrite）的自动化概念验证。纯 CLI 工具，实现文本空隙检测、风格评分、自动生成写作提示和交互式 3R 会话循环。 | Python 3，仅标准库 |
| **p02-writing-html** | 3R 写作工作台桌面 UI 的单文件 HTML 原型集。分别验证三栏自适应布局、Markdown 编辑器、评审报告卡片、空隙标记+情境引导面板、改写看板，最终整合为合成工作台。 | 纯 HTML5/CSS3/ES6，零外部依赖，暗色主题 |
| **prototype** | 早于 p01/p02 的 UI 探索原型。围绕"起承转合"叙事框架展示好/坏文章评审的并排布局，为后续 3R 框架提供设计参考。 | 纯 HTML/CSS，浅色主题，静态页面 |
| **write-agent-studio** | 文档智能体 Flutter 桌面应用。实现人与 AI 围绕 Markdown 文档的协作编辑，三源状态模型（文件/编辑器/AI），内置 AI 对话面板，自适应宽/窄屏布局。 | Dart/Flutter 3.x，flutter_bloc，http 包，Material 3，OpenCode AI 后端 |

## src/ — 各子项目概括

| 子目录 | 思路概括 | 技术栈 |
|--------|---------|--------|
| **cli** | 基于范畴论的写作工作流引擎。将写作过程建模为自由范畴（free quiver），通过 Lean 4 形式化模型 → contract.yaml → 有界展开引擎 → 可执行 FSM 的架构管线，实现阶段转换的形式化验证。 | Rust（pr4xis FSM 引擎，serde/serde_yaml），Lean 4 形式化模型，Kani 符号验证 |
| **provider** | 写作云后端 API 服务。接收文章投稿，通过 LLM（DeepSeek）进行叙事结构分析（起承转合标记），积累优秀文章语料库进行风格对比，返回结构化评审报告。Docker 部署。 | Python 3.11+，FastAPI，pydantic-settings，quanttide-agent（DeepSeek），uv 打包 |
| **studio** | 写作评审 Flutter 前端客户端。提供文章提交表单，调用 provider 的 /review 接口获取分析结果，以颜色编码展示段落叙事标签、分析和风格对比，列出改进建议。多平台支持。 | Dart/Flutter，Material 3，http 包，支持 macOS/iOS/Linux/Web |
