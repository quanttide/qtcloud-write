# ROADMAP

当前阶段：后端 API 已完成 Style 驱动的 3R 重写。下一阶段是前端对接和 Harness 基础设施。

## P0 — 前端对接

- [ ] Flutter 评审面板展示真实 dimension_alignments（分数 + 偏差列表）
- [ ] Flutter 评审面板展示 deviations 的 suggested_alignment
- [ ] 编辑器输入文本发送到 Provider 进行评审的完整链路
- [ ] 删除 `LocalAnalysisService`（离线模式不再有意义）

## P0 — Harness 基础设施

- [ ] `call_llm()` 封装 Harness 层：重试（502/429）、超时（60s）、日志
- [ ] 集成测试通过 Harness 日志接口验证 LLM 调用次数
- [ ] 失败快照：异常时输出完整 prompt + response

## P1 — 评估能力

- [ ] `POST /evaluate` — 接受 text + 多个风格，返回每个风格的匹配度
- [ ] Studio 加载样本从 Provider 获取（不再硬编码）

## P2 — 风格管理

- [ ] `GET /styles` / `POST /styles` — 风格注册和查询
- [ ] 内置风格库

## 不做

- 不接入 OpenCode 对话
- 不做用户系统
- 不重构 Rust CLI
