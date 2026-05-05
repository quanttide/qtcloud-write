# Changelog

## [0.1.0-alpha.2] - 2026-05-05

### Fixtures

- Style 分类重构为读者视角：index.md 入口 + essay/story/brochure 独立定义
- Brochure 定义更新为"被说服决策"（读者视角）
- Essay 定义扩展：覆盖外部现象分析（bad1、bad3、bad5、bad6）
- good/bad 按风格重组到 content/ 下（essay/story/brochure）
- 废弃 plan.md 删除

### Docs

- Review 从单一评分扩展为分类+分级活动
- 新增 classify.md：识别文章叙事风格
- 新增 grade.md：含写得差的人（逐项评分+对照）和写得好的人（风格画像）两个用户故事

## [0.1.0-alpha.1] - 2025-05-03

### Testing

- Provider 单元测试（4 个测试用例）
- 端到端集成测试：真实 Provider + Flutter Web 客户端
- 测试脚本 `scripts/run-tests.sh`：静态分析 → 单元测试 → 集成测试

### Docs

- BRD: 业务需求文档
- PRD: 产品需求文档（aware + review）
- IxD: 交互设计文档
- QA: 质量评估文档对齐直觉框架
- ADD: 架构决策记录
- PMD: 项目管理与路线图
- Fixtures: 11 篇示例文章（5 好 + 6 坏）及对应评审
- ROADMAP: 验证 AI 评审有用性
