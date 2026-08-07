# Changelog

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
