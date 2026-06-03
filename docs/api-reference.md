# API Reference

Base URL: `http://localhost:9000`

## Authentication

本 API 无需请求端认证。后端通过环境变量 `DEEPSEEK_API_KEY` 或 `LLM_API_KEY` 配置 DeepSeek 访问密钥。

## 端点

---

### `POST /review` — 评审文章

提交文章段落，返回每段的叙事结构分析和风格对比。

**请求 `application/json`**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 文章标题 |
| `paragraphs` | array<string> | 是 | 段落列表，每段为一个字符串 |
| `author` | string | 是 | 作者标识 |
| `tag` | string | 是 | 文章类型：`good`（风格样本）/ `bad`（待评审）/ `external`（外部参考） |

**响应 `200`**

| 字段 | 类型 | 说明 |
|------|------|------|
| `article_title` | string | 文章标题 |
| `author` | string | 作者 |
| `tag` | string | 文章类型 |
| `summary` | string | 评审结论摘要 |
| `paragraphs` | array\<ParagraphReview\> | 每段的分析结果 |
| `is_style_available` | bool | 是否已积累风格样本 |
| `suggestions` | array\<Suggestion\> | 改进建议列表 |

**ParagraphReview**

| 字段 | 类型 | 说明 |
|------|------|------|
| `original` | string | 段落原文 |
| `analysis` | string | 叙事功能分析 |
| `tag` | string | 叙事角色：`起` / `承` / `转` / `合` |
| `comparison` | Comparison? | 与风格样本的对比结果（可为 null） |

**Comparison**

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | `good` / `bad` / `pass` |
| `issue` | string? | 问题描述（type=bad 时） |
| `demo` | string? | 示范写法（type=bad 时） |

**Suggestion**

| 字段 | 类型 | 说明 |
|------|------|------|
| `priority` | int | 优先级，1 最高 |
| `action` | string | 操作名称 |
| `detail` | string | 操作说明 |

**示例**

```bash
curl -X POST http://localhost:9000/review \
  -H "Content-Type: application/json" \
  -d '{
    "title": "咖啡厅重逢",
    "paragraphs": ["他推开门走了出去。", "第二天，他又来了。"],
    "author": "test",
    "tag": "bad"
  }'
```

```json
{
  "article_title": "咖啡厅重逢",
  "author": "test",
  "tag": "bad",
  "summary": "风格还在积累中，暂无法对比好/坏。",
  "paragraphs": [
    {
      "original": "他推开门走了出去。",
      "analysis": "动作描写引入场景",
      "tag": "起",
      "comparison": null
    }
  ],
  "is_style_available": false,
  "suggestions": []
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
  -d '{"text": "他推开门走了出去。"}'
```

```json
[
  {
    "gap_type": "action_gap",
    "location": "开门后缺少衔接",
    "line": 1,
    "detail": "动作完成后直接结束段落",
    "structure": "叙事断裂",
    "psychology": "人物反应缺失",
    "reader": "期待落空",
    "craft": "无意识忽略",
    "root_cause": "动作描写不完整"
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

## 数据模型映射

| Provider（Pydantic） | Flutter（Dart） | 契约测试 |
|----------------------|-----------------|---------|
| `ReviewOut` | `DeepReview` | 两端 |
| `ParagraphReview` | `DeepParagraphReview` | Flutter fromJson |
| `Comparison` | `DeepComparison` | Flutter fromJson |
| `Suggestion` | `DeepSuggestion` | Flutter fromJson |
| `GapAnalysis` | 未映射 | Python 响应形状 |
| `RewriteOut` | 未映射 | Python 响应形状 |
| `CycleOut` | 未映射 | Python 响应形状 |

## 契约测试

| 侧 | 文件 | 验证内容 |
|----|------|---------|
| Flutter | `test/writing/provider_contract_test.dart` | `DeepReview.fromJson` 解析完整/含 comparison/空/null 四种 JSON |
| Python | `tests/test_contract.py` | 响应包含所有必需字段，字段值域正确 |

修改数据模型后需同步更新两侧测试，两端均通过后才能合并。
