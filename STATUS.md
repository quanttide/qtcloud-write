# STATUS

## src/provider — 写作云后端 API

**定位**：Style 驱动的叙事分析引擎。接受文本 + 风格定义（dimensions + excerpts），按维度输出对齐分数和偏差。

**现状**：
- `POST /review` — 评估文本与风格的匹配度，每个维度输出 alignment_score + deviations
- `POST /analyze` — 深度分析单个维度的偏差，输出 original/expected pattern 对比 + fix_strategies
- `POST /inspire` — 生成多条启发式修改建议，支持 variety / target_dimensions 参数
- Style 模型：`{name, title, description, dimensions[], excerpts[]}`
- Sample 模型已定义（独立，暂未接入）
- 6 单元测试（`tests/`，mock call_llm）+ 14 集成测试（`integrated_tests/`，真实 DeepSeek API）
- 集成测试验证业务逻辑：匹配风格分高、不匹配分低、中性文本低分、交叉验证
- SQLite 持久化（`data/store.db`）+ 日志轮转（`data/provider.log`）
- 支持 `DEEPSEEK_API_KEY` / `LLM_API_KEY` 环境变量
- 22 测试（6 单元 + 14 集成 + 2 验收）

**未完成**：
- `call_llm()` 裸调 LLM，无重试 / 超时 / token 追踪
- `style.samples` 字段暂未接入 prompt
- 集成测试跳过仅检查 env var，不区分"没 Key"和"Key 错误"

## src/studio — 写作评审 Flutter 前端

**定位**：写作评审桌面客户端（Linux）。

**现状**：
- 3R 工作台：三栏布局、编辑器、Markdown 预览、评审面板
- 评审走统一 `AnalysisService` 接口，调 Provider API
- `RemoteAnalysisService`（HTTP）+ `LocalAnalysisService`（无分析，仅展示占位）
- 125 单元测试 + 6 集成测试

**未完成**：
- 所有评审结果显示的是占位文字，未真实对接 Provider 返回的 dimension_alignments
- 样本文本硬编码在 `writing_review_cubit.dart` 中
- Reflect/Inspire 标签页无 UI（仅占位文字）

## src/cli — 写作工作流引擎 (Rust)

**定位**：待定。当前为 demo 状态。

**现状**：
- CLI demo 可运行标准写作流程
- 与 provider / studio 未集成

## 已知架构问题

### LLM 调用裸奔

`call_llm()` 直接调 `LLM.complete()`，无重试、无超时、无 token 追踪。502 直接抛异常。60s 以上请求可能挂死。参见 `docs/roadmap/harness.md` 的改造方向。

### 集成测试无法在 CI 运行

14 个集成测试需要真实 DeepSeek API Key。当前跳过策略只检查 env var，无法在 CI 中安全执行。需要在 CI 中维护一个测试专用 Key 或提供 mock 模式。

### Flutter 端未对接新 API

3R 标签页显示占位文字而非真实的 dimension_alignments。评审结果不展示。这是目前最大的产品缺口——后端能跑了，前端看不到。
