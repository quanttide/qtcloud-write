# organize.rs — 组织:主题分组

## 职责

实现产物链的 **02 分组**:LLM 从日志中提取主题并为每条条目建议归属(写入日志 YAML),然后生成**分组产物** `groups/<主题>.md`——分组不是中间态,而是下游 distill 的实际输入。

## 流程

```
读全部日志 → 收集未标注条目 → LLM 建议主题(YAML) → 写日志 front matter
            → 重新读 YAML(含人工修改) → 生成 groups/<主题>.md
```

## 核心函数

| 函数 | 说明 |
|------|------|
| `run_llm(prompt)` | 统一 LLM 入口(quanttide-agent,读 `DEEPSEEK_API_KEY`);organize/distill/express 共用 |
| `build_prompt(journals)` | 只把**未标注**条目发给 LLM,要求输出 YAML 归属 |
| `parse_llm_output(text)` | 解析 LLM 输出(容忍 ```yaml 围栏与缺失的 `---`) |
| `organize(workdir)` | 执行主题提取与 YAML 写入,返回更新的条目数 |
| `write_groups(workdir)` | 按最新 YAML 归属聚合条目 → `groups/<主题>.md`,幂等重建 |

## 分组产物格式

```markdown
---
topic: 创作动机
sources:
  - journal/2026-08-15.md#创作日志1
---

(条目原文)

> 来源:journal/2026-08-15.md#创作日志1
```

## 设计思路

1. **LLM 只给建议,决策在人**:`organize` 只写入**未标注**条目(`!jf.fm.topics.contains_key(id)`),人工在 YAML 中写过的归属永不被覆盖——"分解主题"是心智过程,不外包给模型。修正归属 = 直接编辑 YAML,或删掉标注后重跑。
2. **分组必须是实际产物**:早期版本 organize 只写 YAML,分组"形同虚设"——distill 自己重新聚合,组织环节没有存在感。改为 `write_groups` 生成独立文件后,02 分组成为 distill 的唯一输入,链路各环节各司其职。
3. **幂等重建**:`write_groups` 每次按最新 YAML 重建所有分组,人工改 YAML 后重跑 organize 即可刷新分组;`organize` 本身在无未标注条目时返回 0(不重复调用 LLM),但分组仍会重建。
4. **归属建议支持两种 key**:LLM 输出 `文件#id`(跨日期无歧义)或纯 `id`(同文件内匹配),解析时兼容。
5. **提示词要求"只输出 YAML"**:输出格式被 frontmatter 解析器直接消费,降低解析失败率;解析失败时明确报错并把原文返回给用户排查。
