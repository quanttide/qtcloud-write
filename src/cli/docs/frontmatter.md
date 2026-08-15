# frontmatter.rs — 极简 YAML front matter 解析/序列化

## 职责

解析与渲染 markdown 文档顶部的 YAML front matter(`---` 包裹的元数据块)。这是"**标注 = 编辑元数据**"原则的基础设施:主题归属、素材来源都以 front matter 承载,人工可以直接用文本编辑器修改。

## 数据模型

```rust
pub struct FrontMatter {
    pub topic: Option<String>,              // 素材/分组自身的主题(标量)
    pub topics: BTreeMap<String, String>,   // 日志条目 id → 主题(映射)
    pub sources: Vec<String>,               // 来源引用列表(如 journal/2026-08-15.md#09-30)
}
```

支持的最小 YAML 子集:

```yaml
---
topic: 创作动机            # 标量
topics:                    # 映射
  "创作日志1": 创作动机
sources:                   # 列表
  - journal/2026-08-15.md#创作日志1
---
```

## 设计思路

1. **手写解析器,零 YAML 依赖**:只需要 `topic`/`topics`/`sources` 三个键的固定结构,手写 ~70 行解析比引入 serde_yaml 更轻、错误更可控。刻意不追求 YAML 全量支持——领域内 front matter 由本工具自己生成,格式是受控的。
2. **parse/render 对称(round-trip)**:`parse` 返回 `(Option<FrontMatter>, String)`(front matter 与正文分离),`render` 负责序列化。对称设计保证"解析 → 修改 → 渲染"无损,测试中直接断言 round-trip 相等。
3. **容错**:无 front matter 的文档返回 `None`,正文原样保留;`topics` 为空时渲染时省略该键,避免空键噪音。
4. **键值规范化**:条目 id 含冒号(`09:30`)时用引号包裹(`"09-30"`),主题名裸值输出(中文无歧义)。

## 为什么不是完整 YAML

日志文件是给人读的 markdown,front matter 只是附带的机器可读标注。完整 YAML 的复杂度(锚点、多行字符串、类型推断)在这里没有用武之地,反而会让"人工编辑标注"变难。
