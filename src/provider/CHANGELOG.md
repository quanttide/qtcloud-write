# Changelog

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
