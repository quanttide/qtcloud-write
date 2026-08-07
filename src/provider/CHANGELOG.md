# Changelog

## [0.1.0-alpha.5] - 2026-06-03

- API 完全重写为 StyleSample 驱动：`POST /review` 接受 `style`（含 dimensions/excerpts），返回 `dimension_alignments[]`
- 新增 `POST /analyze`：深度分析特定维度偏差，返回 root_cause / fix_strategies
- 新增 `POST /inspire`：生成多个启发式修改建议，支持 variety/target_dimensions 参数
- 删除旧模型：`ArticleIn` / `ReviewOut` / `ParagraphReview` / `Comparison` / `Suggestion` / `CycleOut`
- 删除旧端点：`POST /cycle`
- 删除 `store.py`（StyleStore 由 SQLite 替代）
- 删除 `services/review.py` / `reflect.py` / `rewrite.py`（逻辑合并到 `main.py`）
- 新增 `integrated_tests/`：14 个真实 LLM 业务逻辑测试
- 新增 `pytest-httpx` 测试依赖
- 测试总数：6 单元 + 14 集成

## [0.1.0-alpha.4] - 2026-06-03

- `StyleStore` 从内存列表改为 SQLite 持久化（`data/store.db`），重启不丢失
- 日志按天轮转写入 `data/provider.log`
- 支持 `DEEPSEEK_API_KEY` 环境变量（兼容 `LLM_API_KEY`）
- 删除 `.env` 和 `.env.example` 文件依赖
- 删除 `hvac` 遗留依赖
- `/review` 端点添加 `try/except` 异常保护
- `GapAnalysis` 新增 `line` 字段（行号）
- 新增契约测试：Flutter `fromJson` 验证 + 响应形状验证
- 22 个测试

## [0.1.0-alpha.3] - 2026-06-03

- 修复 LLM 集成：缺失 `_build_analyze_prompt` 等 4 个函数补齐，`.chat()` → `.complete()`
- 合并 3R 端点：新增 `/reflect`（空隙分析）、`/rewrite`（全文改写）、`/cycle`（一站式 3R）
- 响应输出统一 JSON 格式（`response_format={"type": "json_object"}`）
- 解开 `style_examples` 硬编码：改为从 StyleStore 读取
- 测试重构：按 app 结构对齐（test_main.py + services/ 子目录），18 个测试

## [0.1.0-alpha.2] - 2026-05-04

- 配置系统重构：pydantic-settings 替代 Vault，LLM_API_KEY 从环境变量读取
- 新增 DeepSeek base_url 默认配置
- 新增 .gitignore 过滤 Python 产物

## [0.1.0-alpha.1] - 2025-05-03

- 实现文章叙事结构分析 API（POST /review）
- 起承转合段落标签自动分配
- 好文章风格积累与坏文章风格对比
- 内存 StyleStore 支持跨请求积累
- CORS 中间件（允许跨域请求）
