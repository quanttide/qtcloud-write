# API Reference

Base URL: `http://localhost:9000`

## Authentication

本 API 无需请求端认证。后端通过环境变量 `DEEPSEEK_API_KEY` 或 `LLM_API_KEY` 配置 DeepSeek 访问密钥。

## 端点

---

### `POST /review` — 评审文章

纯无状态。提交文章段落和可选风格样本，返回每段的叙事结构分析和风格对比。后端不保存任何状态。

**请求 `application/json`**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 文章标题 |
| `paragraphs` | array<string> | 是 | 段落列表，每段为一个字符串 |
| `style_samples` | array\<StyleSample\> | 否 | 风格样本，用于与文章段落做对比。不传则不返回 comparison |
| `options` | ReviewOptions | 否 | 可选配置 |

**StyleSample**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 样本名称，会出现在响应 `style_usage` 中 |
| `paragraphs` | array<string> | 是 | 样本段落 |

**ReviewOptions**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `include_suggestions` | boolean | 否 | 是否生成改进建议，默认 true |
| `max_paragraphs_to_compare` | int | 否 | 最多对比段落数，默认全部 |

**响应 `200`**

| 字段 | 类型 | 说明 |
|------|------|------|
| `article_title` | string | 文章标题 |
| `summary` | string | 评审结论摘要 |
| `paragraphs` | array\<ParagraphReview\> | 每段的分析结果，与输入段落顺序一致 |
| `suggestions` | array\<Suggestion\> | 改进建议列表 |
| `style_usage` | StyleUsage? | 风格样本使用情况。未传 `style_samples` 时不返回此字段 |

**ParagraphReview**

| 字段 | 类型 | 说明 |
|------|------|------|
| `index` | int | 段落序号（从 0 开始，对应输入 `paragraphs` 的索引） |
| `original` | string | 段落原文 |
| `analysis` | string | 叙事功能分析 |
| `tag` | string | 叙事角色：`起` / `承` / `转` / `合` |
| `comparison` | Comparison? | 与风格样本的对比结果。未传 `style_samples` 时不返回此字段 |

**Comparison**

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | `good` / `bad` / `pass` / `no_style` |
| `issue` | string? | 问题描述（type=bad 时） |
| `demo` | string? | 示范写法（type=bad 时） |

**Suggestion**

| 字段 | 类型 | 说明 |
|------|------|------|
| `priority` | int | 优先级，1 最高 |
| `action` | string | 操作名称 |
| `detail` | string | 操作说明 |
| `paragraph_index` | int? | 关联段落序号（可为 null，表示全局建议） |

**StyleUsage**

| 字段 | 类型 | 说明 |
|------|------|------|
| `samples_used` | array\<string\> | 实际参与对比的样本名称列表 |
| `confidence` | number | 对比置信度（0-1） |

**示例 — 无风格样本**

```bash
curl -X POST http://localhost:9000/review \
  -H "Content-Type: application/json" \
  -d '{
    "title": "咖啡厅重逢",
    "paragraphs": ["他推开门走了出去。", "第二天，他又来了。"]
  }'
```

```json
{
  "article_title": "咖啡厅重逢",
  "summary": "两段叙事，第一段动作开篇，第二段时间跳跃。",
  "paragraphs": [
    {
      "index": 0,
      "original": "他推开门走了出去。",
      "analysis": "以动作开篇，简洁有力。",
      "tag": "起"
    },
    {
      "index": 1,
      "original": "第二天，他又来了。",
      "analysis": "时间跳跃，缺少过渡。",
      "tag": "承"
    }
  ],
  "suggestions": []
}
```

**示例 — 带风格样本**

```bash
curl -X POST http://localhost:9000/review \
  -H "Content-Type: application/json" \
  -d '{
    "title": "咖啡厅重逢",
    "paragraphs": ["他推开门走了出去。"],
    "style_samples": [
      {
        "name": "细腻描写风格",
        "paragraphs": ["他轻轻推开门，冷风裹着雨丝扑面而来。他深吸一口气，迈步走进雨里。"]
      }
    ]
  }'
```

```json
{
  "article_title": "咖啡厅重逢",
  "summary": "动作描写偏简略，可增加环境细节。",
  "paragraphs": [
    {
      "index": 0,
      "original": "他推开门走了出去。",
      "analysis": "以动作开篇，简洁有力。",
      "tag": "起",
      "comparison": {
        "type": "bad",
        "issue": "动作描写缺少环境细节",
        "demo": "他推开门，冷风裹着雨丝扑面而来。"
      }
    }
  ],
  "suggestions": [
    {
      "priority": 1,
      "action": "补充环境描写",
      "detail": "第一段可在动作后加入环境细节，增强沉浸感",
      "paragraph_index": 0
    }
  ],
  "style_usage": {
    "samples_used": ["细腻描写风格"],
    "confidence": 0.82
  }
}
```

---

### `POST /reflect` — 空隙诊断

检测文本中的叙事空隙，从多个维度分析深层原因。

**请求 `application/json`**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | 是 | 待分析文本，最长 8000 字符 |

**响应 `200`**

返回 GapAnalysis 数组。

| 字段 | 类型 | 说明 |
|------|------|------|
| `gap_type` | string | 空隙类型：`time_jump` / `dialog_gap` / `action_gap` / `perspective_shift` / `transition` |
| `location` | string | 位置描述 |
| `line` | int | 所在行号（1-based），无法确定时为 0 |
| `detail` | string | 问题说明 |
| `structure` | string | 叙事结构角度归因 |
| `psychology` | string | 人物心理角度归因 |
| `reader` | string | 读者期待角度归因 |
| `craft` | string | `有意识留白` 或 `无意识忽略` |
| `root_cause` | string | 根本原因总结 |

**示例**

```bash
curl -X POST http://localhost:9000/reflect \
  -H "Content-Type: application/json" \
  -d '{"text": "他推开门走了出去。第二天，她又来了。"}'
```

```json
[
  {
    "gap_type": "time_jump",
    "location": "从开门到第二天",
    "line": 2,
    "detail": "时间跳过没有过渡",
    "structure": "节奏过快",
    "psychology": "人物情绪中断",
    "reader": "跟不上时间线",
    "craft": "无意识忽略",
    "root_cause": "缺少时间过渡标记"
  }
]
```

---

### `POST /rewrite` — 全文改写

基于空隙诊断结果，重新改写文章。

**请求 `application/json`**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | 是 | 待改写文本，最长 8000 字符 |

**响应 `200`**

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | string | 改写后的完整文本 |
| `length` | int | 改写文本长度 |

**示例**

```bash
curl -X POST http://localhost:9000/rewrite \
  -H "Content-Type: application/json" \
  -d '{"text": "他推开门走了出去。"}'
```

```json
{
  "text": "他推开门走了出去。冷风扑面而来。他裹紧外套，深吸了一口气。",
  "length": 38
}
```

---

### `POST /cycle` — 完整 3R 流程

一次调用完成评审 → 空隙诊断 → 改写，返回三轮结果。

**请求 `application/json`**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | 是 | 待分析文本，最长 8000 字符 |

**响应 `200`**

| 字段 | 类型 | 说明 |
|------|------|------|
| `review` | Review3ROut | 评审结果 |
| `reflect` | array\<GapAnalysis\> | 空隙诊断结果 |
| `rewrite` | RewriteOut | 改写结果 |

**Review3ROut**

| 字段 | 类型 | 说明 |
|------|------|------|
| `genre` | string | 场景体裁分类 |
| `intent` | string | 作者创作意图 |
| `stage` | string | 完成度判断 |
| `summary` | string | 一句话总结 |

**示例**

```bash
curl -X POST http://localhost:9000/cycle \
  -H "Content-Type: application/json" \
  -d '{"text": "他推开门走了出去。第二天，她又来了。"}'
```

```json
{
  "review": {
    "genre": "重逢场景",
    "intent": "营造暧昧氛围",
    "stage": "初稿，动作线完整但心理描写不足",
    "summary": "两人在咖啡厅重逢的片段"
  },
  "reflect": [
    {
      "gap_type": "time_jump",
      "location": "从开门到第二天",
      "line": 2,
      "detail": "时间跳过没有过渡",
      "structure": "节奏过快",
      "psychology": "人物情绪中断",
      "reader": "跟不上时间线",
      "craft": "无意识忽略",
      "root_cause": "缺少时间过渡标记"
    }
  ],
  "rewrite": {
    "text": "他推开门走了出去。那一夜他辗转难眠。第二天，她又来了。",
    "length": 32
  }
}
```

## 错误处理

所有端点在异常时返回 502 Bad Gateway，不返回 500。

```json
{
  "detail": "LLM 调用失败: chat failed after retries"
}
```

常见错误：

| 错误场景 | detail 示例 |
|----------|-------------|
| API key 未配置 | `请配置 LLM_API_KEY 或 DEEPSEEK_API_KEY 环境变量` |
| DeepSeek 调用失败 | `LLM 调用失败: chat failed after retries` |
| 输入过长 | 422 Unprocessable Entity（FastAPI 自动校验） |

## 无状态原则

`/review` 是纯无状态端点：

- 后端不存储任何请求数据
- 风格对比完全依赖请求中传入的 `style_samples`
- 同一请求重复发送应返回一致结果（LLM 输出可能有微小波动）
- 无需清理缓存或重置状态

## 数据模型映射

| Provider（Pydantic） | Flutter（Dart） | 契约测试 |
|----------------------|-----------------|---------|
| `ReviewOut` → 新增 `style_usage`, 移除 `is_style_available` | `DeepReview` | 两端 |
| `ParagraphReview` → 新增 `index` | `DeepParagraphReview` | Flutter fromJson |
| `Comparison` | `DeepComparison` | Flutter fromJson |
| `Suggestion` → 新增 `paragraph_index` | `DeepSuggestion` | Flutter fromJson |
| `StyleUsage` | 新增 | — |

## 契约测试

| 侧 | 文件 | 验证内容 |
|----|------|---------|
| Flutter | `test/writing/provider_contract_test.dart` | `DeepReview.fromJson` 解析各种合法 JSON |
| Python | `tests/test_contract.py` | 响应包含所有必需字段，字段值域正确 |

修改数据模型后需同步更新两侧测试，两端均通过后才能合并。
