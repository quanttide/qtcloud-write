# ROADMAP — 写作云

## 目标

让 **"评审" = AI**（不是正则），且这条链路在任何环境都能验证。

## 当前诊断

当前项目处于"双管线"状态：前端正则引擎 + 后端 LLM 引擎各自独立运行、互不调用、结果不一致。五个系统性盲区需逐个消除：

| # | 盲区 | 影响 |
|---|------|------|
| 1 | 前端不调后端，后端不服务前端 | 用户看到的评审结果来自正则，不是 AI |
| 2 | `autouse=True` mock 了整个 LLM 调用链 | 152 个测试全绿，但没一个验证 AI 输出 |
| 3 | `DeepAnalysisService?` 可空 = 壳没有截止时间 | "深度分析"按钮存在半年仍是空壳 |
| 4 | 正则可离线跑，导致开发者从不启动后端 | 开发环境和生产环境行为完全不一致 |
| 5 | 前后端各自定义空隙行号/类型/结果格式 | 概念同名但数据不同，前端无法消费后端输出 |

## 行动

### P0 — 统一管线（消除盲区 1、4）

- [ ] `runReview()` 的 provider 路径改为**同步必走**（不再 try/catch 静默降级），provider 不可用时评审按钮直接禁用并提示"启动 provider 后再评审"
- [ ] 去掉 `AnalysisEngine.analyze()` 作为 `runReview()` 的回退路径（不再走正则）
- [ ] `isUsingProvider` 展示到 UI（底部状态栏或结果面板头部），用户明确知道当前是"AI 分析"还是"本地分析（离线）"
- [ ] 合并三 Tab 为一个结果面板：评审按钮只调 `/cycle`，返回 unified 结果展示在单一面板
- [ ] `docker compose up` 一键启动全套
- [ ] `scripts/deploy-local.sh` 增加健康检查：等待 provider 就绪后再启动 studio
- [ ] 删掉 `AnalysisEngine.analyze()`（正则引擎不再作为评审路径）

### P0 — 测试分层（消除盲区 2）

- [ ] 单元测试：保留 prompt 构建、JSON 解析的纯逻辑测试（mock LLM 返回）
- [ ] 集成测试：mock DeepSeek HTTP 层（用 `responses` 或 `httpx_mock`），保留 `analyze_paragraph` / `compare_with_style` 不被 mock
- [ ] 集成测试：Flutter 端调用 provider 的 HTTP 路径（mock provider），不 mock cubit 内部
- [ ] 验收测试（CI 可选）：用真实 DeepSeek API + 固定 prompt，验证输出格式符合 schema
- [ ] 删掉 `conftest.py` 中的 `autouse=True` mock，替换为按需 mock

### P1 — 必填桩服务（消除盲区 3）

- [ ] `DeepAnalysisService` 改为必填参数（非可空），`main.dart` 注入一个 `LocalFallbackService` 实现同样的接口
- [ ] `LocalFallbackService` 返回 501 错误 + "provider 未启动"提示，不在 UI 中显示任何分析结果按钮
- [ ] 删除 `hasDeepService` getter，废弃的"深度分析"按钮代码
- [ ] 规范化 tag 标记：`// INTEGRATION_REQUIRED` 或 `// STUB`，CI 中 grep 到则警告

### P1 — 数据契约统一（消除盲区 5）

- [ ] 定义 `GapAnalysis` 共享 schema（JSON Schema 或 proto），Dart 和 Python 从同一文件生成
- [ ] Flutter 端删除 `models/analysis.dart`（正则模型），统一使用 `deep_analysis.dart`（provider 模型）
- [ ] 后端 `/reflect` 返回的 `line` 字段改为必填（当前是 `line: int = 0`）
- [ ] 后端 `location` 字段格式标准化：`"L{line}: {人类可读描述}"`

### P2 — 体验打磨

- [ ] Provider 可用时，评审结果展示起承转合段落分析 + summary
- [ ] 编辑器空隙标记列在 Provider 模式下标记来自后端的 gap line 数据
- [ ] 多轮迭代：Cubit 维护评分历史，展示简单趋势

## 不做的

- 不接入 OpenCode 对话
- 不做用户系统 / 多文档管理
- 不保存评审历史到数据库
