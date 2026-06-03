# 前后端 API 契约

Flutter (`src/studio`) 和 Provider (`src/provider`) 之间的数据模型约定。违反此契约会导致 CI 中对应的契约测试失败。

## 字段命名

| 侧 | 风格 | 示例 |
|---|------|------|
| Provider（Python） | snake_case | `article_title` |
| Flutter（Dart） | camelCase（fromJson 中映射） | `articleTitle` |
| 网络传输 | snake_case | `article_title` |

Flutter 的 `fromJson` 负责将 snake_case JSON 映射为 camelCase 字段。Provider 不应输出 camelCase。

## 端点

### `POST /review`

请求：

```json
{
  "title": "string",
  "paragraphs": ["string"],
  "author": "string",
  "tag": "good | bad | external"
}
```

响应：

```json
{
  "article_title": "string",
  "author": "string",
  "tag": "string",
  "summary": "string",
  "paragraphs": [
    {
      "original": "string",
      "analysis": "string",
      "tag": "起 | 承 | 转 | 合",
      "comparison": {
        "type": "good | bad | pass",
        "issue": "string | null",
        "demo": "string | null"
      }
    }
  ],
  "is_style_available": false,
  "suggestions": [
    {
      "priority": 1,
      "action": "string",
      "detail": "string"
    }
  ]
}
```

### `POST /reflect`

请求：

```json
{
  "text": "string"
}
```

响应：

```json
[
  {
    "gap_type": "time_jump | dialog_gap | action_gap | perspective_shift | transition",
    "location": "string",
    "line": 0,
    "detail": "string",
    "structure": "string",
    "psychology": "string",
    "reader": "string",
    "craft": "有意识留白 | 无意识忽略",
    "root_cause": "string"
  }
]
```

### `POST /rewrite`

请求：

```json
{
  "text": "string"
}
```

响应：

```json
{
  "text": "string",
  "length": 0
}
```

### `POST /cycle`

请求：

```json
{
  "text": "string"
}
```

响应：

```json
{
  "review": {
    "genre": "string",
    "intent": "string",
    "stage": "string",
    "summary": "string"
  },
  "reflect": [ /* GapAnalysis 数组 */ ],
  "rewrite": {
    "text": "string",
    "length": 0
  }
}
```

## 数据模型对应

| Provider (Python Pydantic) | Flutter (Dart) | 契约测试 |
|---|---|---|
| `ReviewOut` | `DeepReview` | 两端均有 |
| `ParagraphReview` | `DeepParagraphReview` | Flutter fromJson |
| `Comparison` | `DeepComparison` | Flutter fromJson |
| `Suggestion` | `DeepSuggestion` | Flutter fromJson |
| `GapAnalysis` | Flutter 暂未映射 | Python 响应形状 |
| `RewriteOut` | Flutter 暂未映射 | Python 响应形状 |
| `CycleOut` | Flutter 暂未映射 | Python 响应形状 |

## 错误处理

所有端点在异常时返回 502，body 格式：

```json
{
  "detail": "错误描述字符串"
}
```

不返回 500。Flutter 端应捕获 502 并显示 `detail` 内容。

## 契约测试维护

| 侧 | 文件 | 验证内容 |
|---|---|---|
| Flutter | `test/writing/provider_contract_test.dart` | `DeepReview.fromJson` 能解析完整/含 comparison/空/null 四种 JSON shape |
| Python | `tests/test_contract.py` | provider 返回的 JSON 包含所有必需字段，tag 值域正确 |

**修改模型时的操作流程**：

1. 修改 Pydantic model → 新增/删除/重命名字段
2. 更新 Dart 侧对应的 `fromJson` 和字段定义
3. 更新 Flutter `provider_contract_test.dart` 中的示例 JSON
4. 更新 Python `test_contract.py` 中的断言
5. 两端的测试都绿才能合并
