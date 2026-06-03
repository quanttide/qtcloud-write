# 量潮创始人实验室 — 概念验证清单

面向写作云（qtcloud-write）的逐项验证序列。

## 分组 & 依赖关系

```
分析层 — src/provider
│
评审标注嵌入编辑器    依赖：p02（复用 UI 模式）、provider API
多文档风格对比       依赖：provider（StyleStore）

编辑层 — src/studio / write-agent-studio
│
p02 写作云 HTML 原型  依赖：无
```

## PoC 清单

| # | PoC | 验证目标 | 验收标准 |
|---|-----|---------|---------|
| 1 | 写作云 HTML 原型 | 在投入 Flutter 之前验证三栏布局 + 3R 循环的桌面交互体验 | 三栏布局、Markdown 编辑、评审面板、情境引导、3R 仪表盘、状态栏六项可运行 |
| 2 | 评审标注嵌入编辑器 | 把 provider 分析结果嵌入编辑器，形成"写作→评审→修改→再评审"闭环 | 空隙标记、叙事标签、侧面板分析、点击跳转、一键重评 |
| 3 | 多文档风格对比 | 可视化对比多篇文章的叙事结构分布，发现作者的写作模式 | 分布热力图、偏差可视化、段落对比对、筛选过滤、趋势图 |

## 推荐实施顺序

| 优先级 | PoC | 预估工作量 | 状态 |
|--------|-----|-----------|------|
| 1 | p02 写作云 HTML 原型 | 小 | 待实现 |
| 2 | 评审标注嵌入编辑器 | 中 | 待实现 |
| 3 | 多文档风格对比 | 小 | 待实现 |

## 技术栈

| 层 | 推荐选择 |
|----|---------|
| 界面原型 | 单 HTML 文件 |
| 界面原型 | 单 HTML 文件（p02/p03/p05） |
| 工作流引擎 | Rust + Lean（p04） |
| 版本控制 | Git（内置） |
| 文档 | MyST Markdown |

## 设计文档索引

- [p02 写作云 HTML 原型](examples/p02-writing-html/README.md)

## 来源

> 写作云蓝图：`docs/memory/roadmap/qtcloud-write.md`
> 创作方法论：`docs/memory/context/write.md`
> 实践记录：`docs/memory/journal/2026-06-02.md`
> 缺口分析：`STATUS.md`
