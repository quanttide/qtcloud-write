# material CLI 模块文档

写作素材收集与整理 CLI(binary `material`)的模块地图与设计思路。每个模块对应一个文档,按需扩展。

## 模块地图

| 模块 | 对应命令 | 职责 | 文档 |
|------|----------|------|------|
| [`main.rs`](../../src/main.rs) | 全部 | CLI 入口:clap 命令解析与分发 | [main.md](main.md) |
| [`lib.rs`](../../src/lib.rs) | — | crate 根,模块声明与 re-export | — |
| [`writing.rs`](../../src/writing.rs) | — | 领域模型:写作的基本单位 `Writing` 与状态机 | [writing.md](writing.md) |
| [`journal.rs`](../../src/journal.rs) | `collect` | 日志:收集、条目解析、front matter 更新 | [journal.md](journal.md) |
| [`organize.rs`](../../src/organize.rs) | `organize` | 组织:LLM 主题提取、YAML 归属、分组产物 | [organize.md](organize.md) |
| [`distill.rs`](../../src/distill.rs) | `distill` | 提取:过滤次要信息 + 统一表达 → 初稿 | [distill.md](distill.md) |
| [`express.rs`](../../src/express.rs) | `express` | 表达:以初稿为底稿,按写作目标 → 定稿 | [express.md](express.md) |
| [`frontmatter.rs`](../../src/frontmatter.rs) | — | 基础设施:极简 YAML front matter 解析/序列化 | [frontmatter.md](frontmatter.md) |

## 产物链

四个命令对应四个阶段,每个阶段一个编号产物:

```
01 收集 ──> 02 分组 ──> 03 初稿 ──> 04 定稿
collect    organize    distill     express
```

| 阶段 | 产物 | 说明 |
|------|------|------|
| 01 收集 | `journal/YYYY-MM-DD.md` | 条目化 + YAML 标注的初步加工版本 |
| 02 分组 | `groups/<主题>.md` | 按主题聚合的条目原文(带来源引用) |
| 03 初稿 | `materials/<主题>.md` | 过滤杂质、统一表达的完整初稿 |
| 04 定稿 | `materials/<主题>-定稿.md` | 按写作目标重构的成品 |

## 设计原则

1. **四命令四阶段**:每个命令只做一个阶段,产物编号稳定,便于归档与回溯。
2. **标注 = 编辑元数据,整理 = 操作文件**:主题归属写入 markdown 的 YAML front matter(人工可直接编辑);聚合/生成通过文件操作完成。编辑对象是 git 管理的 markdown 文档。
3. **LLM 只给建议,决策在人**:`organize` 的主题归属是可编辑的建议;过滤与定稿的提示词采用**通用判据**,不针对特定文本优化。
4. **初稿必须有用**:过滤只删四类明确杂质,信息宁可完整不可削减——初稿是定稿的底稿,信息不完整会直接拉低定稿质量。
5. **LLM 接入统一**:所有 LLM 调用经 `organize::run_llm`(quanttide-agent),读 `DEEPSEEK_API_KEY`。
