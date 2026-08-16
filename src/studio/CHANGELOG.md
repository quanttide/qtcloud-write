# Changelog

## [0.1.0-alpha.4] - 2026-08-16

- **方向替换**：丢弃 3R 评审工作台（review/reflect/rewrite），移植 qtfounder 新版 AI 原生写作编辑器
- 核心原则：AI 只产出结构（元数据），绝不改写原文；`.analysis/` 缓存删除即还原
- 四阶段工作流对齐 CLI 四命令：01_收集（journal/）→ 02_分组（groups/）→ 03_初稿（materials/）→ 04_定稿（materials/-定稿.md）
- 三栏编辑器：章节阶段树 + 纯文本编辑区 + 只读标注层（拆分虚线/场景色条，点击跳行）+ AI 整理面板
- 分阶段分析方法：01_收集 灵感分解（采纳 → 02_分组 原样摘录）；其他阶段 结构分析（标签/摘要/拆分建议/场景/归类建议）
- 负反馈机制：忽略的建议注入下次 prompt 不再提出；分析缓存复用 + 强制刷新
- 编辑器：3 秒防抖自动保存、去 Markdown 字数统计、脏标记、光标位置
- LLM：DeepSeek API（`DEEPSEEK_API_KEY`），temperature 0.2，8k 截断，JSON 容错解析
- 18 单元测试（bloc / repository / overlay / widget）

## [0.1.0-alpha.3] - 2026-06-03

- 统一分析管线：`AnalysisService` 接口 + `RemoteAnalysisService` / `LocalAnalysisService`
- 评审按钮优先调 Provider LLM，不可用时回退本地正则，UI 标注分析来源
- 删除独立"深度分析"按钮，合并到"评审"
- `AnalysisService` 改为构造时必填，不再可空
- 删除 `state.analysis` / `state.gapCount` / `state.avgScore` 等正则字段
- 新增契约测试：Flutter `fromJson` 验证 + Python 响应形状验证
- 删除 `analysis_engine.dart` 作为评审回退路径
- 3R 标签页合并方向：评审结果统一展示在一个面板
- 124 单元测试 + 6 集成测试

## [0.1.0-alpha.2] - 2026-06-03

- 3R 写作工作台：三栏布局 + 编辑器 + 空隙标记列 + 分析面板
- 正则分析引擎：4 类空隙检测 / 3 项风格评分 / 引导问题 / 改写建议
- Markdown 编辑/预览切换
- BLoC 状态管理
- 设计令牌暗色主题
- 深度分析入口：连接 provider 语义分析（--dart-define=PROVIDER_URL）
- doc_agent 文档智能体组件保留
- 单元测试 124 个 + 集成测试 9 个

## [0.1.0-alpha.1] - 2025-05-03

- Flutter Web 写作评审客户端界面
- 文章提交表单（标题、作者、标签、正文）
- 评审结果展示：段落标签彩色标识、风格对比高亮、修改建议列表
- API_URL 通过 --dart-define 注入，支持多环境
