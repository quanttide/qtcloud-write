# writing.rs — Writing 聚合根(领域模型)

## 职责

定义写作云的基本单位 `Writing` 及其状态模型——这是 material 命令背后的领域概念,与"文档云的基本单位 `Document`"形成产品线对照:写作云的产物是"写作",而非"文档"。

## 数据模型

```rust
pub enum WritingStatus {
    Material,   // 素材:灵感碎片、收集的引用与材料
    Outline,    // 大纲:结构规划
    Draft,      // 草稿:正文写作
    Final,      // 定稿:完成
}

pub struct Writing {
    pub id: String,
    pub status: WritingStatus,
}
```

## 设计思路

1. **线性四阶段状态机**:`Material → Outline → Draft → Final`,只前进不后退(`advance()` 在 `Final` 后返回 `None`)。新模型刻意不引入旧 CLI 的 review/reflect/rewrite 循环与计数——那是已被否决的范畴论路线(material → outline → firstDraft → finalDraft + 循环守卫),完整旧实现见 git 历史 `b47f0b6`。
2. **行为痕迹的隐喻**:`Writing` 的词源是"划、刻"——文本是写作行为的延伸,素材、便签、草稿皆是 writing。这个隐喻与**过程模型**(描述"创作走到哪一步")同构,所以四阶段全程自洽;而 `Work`(作品)是完成模型("a work" 默认已完成),material 阶段的素材在语义上断裂。`Manuscript`(手稿)同理,在素材期与定稿后都断裂。命名决策链:Article ✗ → Document ✗ → Work △ → **Writing ✓**。
3. **最小模型**:早期版本曾包含 `WritingKind`(Article/Book),后按"暂不预设形态"移除——形态(文章/书/剧本)需要时以扩展方式加入,不占用当前状态机。
4. **与 material 命令的关系**:material 四阶段产物链(收集/分组/初稿/定稿)是写作流程的**工具侧**;`WritingStatus` 是**领域侧**的状态刻画。两者同构但不强行绑定——material 命令处理的具体产物(日志、分组、素材)未来可挂接到 `Writing` 实体上作为其状态迁移的证据。

## 典型用法

```rust
let mut w = Writing::new("w1");
assert_eq!(w.status, WritingStatus::Material);
w.advance(); // → Outline
```
