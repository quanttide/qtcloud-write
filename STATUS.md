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

## src/studio — AI 原生写作编辑器 (Flutter)

**定位**：写作云桌面端写作工作台（Linux），与 CLI 四命令共享数据目录。

**现状**：
- 四阶段工作流：01_收集（journal/）→ 02_分组（groups/）→ 03_初稿（materials/）→ 04_定稿（materials/-定稿.md）
- 三栏编辑器：章节阶段树 + 纯文本编辑区 + 只读标注层（拆分线/场景色条）+ AI 整理面板
- AI 只产元数据不改写原文：`.analysis/` 缓存删除即还原，负反馈 + 缓存复用
- **客户端复现 CLI 四命令**：流程操作面板执行 collect/organize/distill/express
  （`lib/workflow/` 为 CLI 逻辑的 Dart 移植，提示词与产物格式一致）
- LLM：DeepSeek API（`DEEPSEEK_API_KEY`，环境代理自动读取）
- 38 单元测试 + 1 真实 LLM 集成测试（无 key 自动跳过）

**未完成**：
- 示例工作目录尚无真实数据（需 CLI 生成）
- 章节搜索 / 预览 / 全屏按钮为空壳
- 阶段推进动作（03 → 04 移动）未接 UI

## src/cli — 写作工作流引擎 (Rust)

**定位**：四命令工作流引擎：collect（收集）→ organize（分组）→ distill（初稿）→ express（定稿）。

**现状**：
- 四命令全实现：journal/ 收集、groups/ 分组、materials/ 初稿与定稿
- 产物为 git 管理的 Markdown + YAML front matter（标注=元数据，整理=操作文件）
- 与 studio 共享同一数据目录（studio 的 FileChapterRepository 映射 CLI 产物目录）

## 已知架构问题

### LLM 调用裸奔

`call_llm()` 直接调 `LLM.complete()`，无重试、无超时、无 token 追踪。502 直接抛异常。60s 以上请求可能挂死。参见 `docs/roadmap/harness.md` 的改造方向。

### 集成测试无法在 CI 运行

14 个集成测试需要真实 DeepSeek API Key。当前跳过策略只检查 env var，无法在 CI 中安全执行。需要在 CI 中维护一个测试专用 Key 或提供 mock 模式。

### Flutter 端未对接新 API

3R 标签页显示占位文字而非真实的 dimension_alignments。评审结果不展示。这是目前最大的产品缺口——后端能跑了，前端看不到。
