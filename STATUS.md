# STATUS

## src/provider — 写作云后端 API

**定位**：AI 驱动叙事分析后端。LLM 分析管线 + 风格积累。

**现状**：
- `/review` `/reflect` `/rewrite` `/cycle` 四个端点可用
- `StyleStore` 内存积累好文章风格语料
- 端点有 error handling（502）
- Dockerfile + Terraform 就绪

**未完成**：
- `quanttide-agent` 未加入 `pyproject.toml` 依赖，首次部署需手动 pip install
- `StyleStore` 纯内存，重启即丢失风格积累
- `/review` 返回的 `summary` 是三段硬编码文本，不随文章内容变化
- 所有集成测试用 `autouse=True` mock 了整个 LLM 调用链，仅验证 HTTP 路由，不验证 AI 分析质量

## src/studio — 写作评审 Flutter 前端

**定位**：写作评审桌面/Web 客户端。

**现状**：
- 提交表单、评审结果展示可用
- API 服务层已分离，通过 `--dart-define=API_URL` 注入后端地址

**未完成**：
- **双分析引擎**：Flutter 端有一套独立的正则分析引擎（`analysis_engine.dart`），后端有一套 LLM 引擎。前端 `runReview()` 优先调用后端，失败时静默回退到正则，用户无法感知当前用的是 AI 还是规则
- **`DeepAnalysisService` 可空**：构造函数默认不注入，`loadSample()` 完全不走后端
- **硬编码样本**：样本文本写在 Dart 文件里，不从 `tests/fixtures/` 加载
- **3R 三 Tab 过重**：Review/Reflect/Rewrite 拆成三个独立面板，用户只需"帮我看稿子"一个操作

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

### 前后端各做一半

Flutter 有 `analysis_engine.dart`（正则），Python 有 `services/review.py`（LLM）。两套都能跑、都有测试、都有 UI，但前端不真正调用后端。新功能必须有从 UI → 网络 → 后端 → LLM → 返回 UI 的全链路测试才能标记完成。

### 测试全绿 ≠ 功能正常

`conftest.py` 用 `autouse=True` mock 了全部 LLM 调用。测试通过只说明 HTTP 路由通，不证明分析质量。验收测试需用真实 LLM（可固定 prompt）。

### 数据契约不统一

前后端对"空隙"的定义不同——前端用 `line: int`（行号），后端用 `location: str`（描述文本）。同一概念在两端表现不一致，前端能跳转到行但后端不返回行号。

### 占位功能无截止时间

可空依赖 + 测试覆盖报错路径 = 技术债被正式化。`DeepAnalysisService?` 的可空设计让编译器不报错，但"深度分析"功能始终未实现。
