# STATUS

## src/provider — 写作云后端 API

**定位**：AI 驱动叙事分析后端。LLM 分析管线 + 风格积累。

**现状**：
- `/review` `/reflect` `/rewrite` `/cycle` 四个端点可用，均有 502 error handling
- `call_llm` / `analyze_paragraph` / `compare_with_style` 三套 LLM 调用路径完整
- `StyleStore` SQLite 持久化（`src/provider/data/store.db`），重启不丢失
- `DEEPSEEK_API_KEY` 和 `LLM_API_KEY` 两种环境变量均支持
- 日志按天轮转写入 `src/provider/data/provider.log`
- Dockerfile + Terraform 就绪
- 18 个测试

**未完成**：
- `/review` 端点返回的 `summary` 是三段硬编码文本（"好文章，叙事结构清晰。" / "风格还在积累中…" / "根本问题不是…"），不随文章内容变化，与 LLM 分析结果无关
- 集成测试用 `autouse=True` mock 了整个 LLM 调用链，仅验证 HTTP 路由和数据格式，不验证 AI 分析质量
- `StyleStore` 无数据迁移/备份机制

## src/studio — 写作评审 Flutter 前端

**定位**：写作评审桌面客户端（Linux）。

**现状**：
- 3R 工作台：三栏布局、编辑器、Markdown 预览、空隙标记
- 评审走统一 `AnalysisService` 接口，优先调后端 LLM，不可用时回退本地正则
- `RemoteAnalysisService`（HTTP）+ `LocalAnalysisService`（正则包装），构造时必填，不可空
- `runReview()` / `loadSample()` 均通过 `AnalysisService`，不再分两条路径
- 深度分析按钮已合并到"评审"，UI 只有一个入口
- 19 个组件、8 个模型、6 个服务、124 单元测试 + 6 集成测试

**未完成**：
- 样本文本仍然硬编码在 `writing_review_cubit.dart` 的 `_sampleText` 中
- Reflect/Rewrite 标签页在后端返回数据前仅展示占位文字，无离线回退内容
- `loadSample()` 在 Provider 不可用时走 `LocalAnalysisService`，但样本文本本身还是硬编码

## src/cli — 写作工作流引擎 (Rust)

**定位**：将写作流程定义为可配置的状态机转换规则。

**现状**：
- CLI demo 可运行标准写作流程
- `contract.yaml` 定义 stage/expand 两层配置
- Lean 4 形式化模型（`WriteCategory.lean`）作为语义锚点

**未完成**：
- 与 provider / studio 尚未集成
- 仅 demo 级别可用，未产品化

## 已知架构问题

### 测试全绿 ≠ AI 可工作

`conftest.py` 用 `autouse=True` mock 了全部 LLM 调用。18 个测试全过只说明 HTTP 路由和数据格式正确，不证明 LLM 能分析出有意义的结论。验收测试应使用真实 LLM（固定 prompt），mock 只该存活一个 PR 周期。

### 后端 summary 与 LLM 无关

`/review` 的 summary 是三段 if/else 硬编码，即使 LLM 正常工作，这个结论也和 LLM 分析结果无关。LLM 返回的 `analysis` 字段仅出现在段落级别，不在文章级别呈现。

### 样本仅存在于前端

测试样本（good/bad 文章）只被 Python 测试使用。Flutter 前端没有从 `tests/fixtures/` 加载样本的入口，也没有从后端获取样本的 API。前后端各有自己的样本数据。
