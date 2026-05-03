# Changelog

## [0.1.0-alpha.1] - 2025-05-03

### Provider

- 实现文章叙事结构分析 API（POST /review）
- 起承转合段落标签自动分配
- 好文章风格积累与坏文章风格对比
- 内存 StyleStore 支持跨请求积累
- CORS 中间件（允许跨域请求）

### Studio

- Flutter Web 写作评审客户端界面
- 文章提交表单（标题、作者、标签、正文）
- 评审结果展示：段落标签彩色标识、风格对比高亮、修改建议列表
- API_URL 通过 --dart-define 注入，支持多环境

### Testing

- Provider 单元测试（4 个测试用例）
- 端到端集成测试：真实 Provider + Flutter Web 客户端
- 测试脚本 `scripts/run-tests.sh`：静态分析 → 单元测试 → 集成测试

### Docs

- BRD: 业务需求文档
- PRD: 产品需求文档（discern + inherit）
- IxD: 交互设计文档
- QA: 质量评估文档对齐直觉框架
- ADD: 架构决策记录
- PMD: 项目管理与路线图
- Fixtures: 11 篇示例文章（5 好 + 6 坏）及对应评审
- ROADMAP: 验证 AI 评审有用性
