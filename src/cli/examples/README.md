# 案例:创始人小说创作日志

**数据来源**:[quanttide/quanttide-fiction-of-founder](https://github.com/quanttide/quanttide-fiction-of-founder)《职场言情》创作日志 1

<https://github.com/quanttide/quanttide-fiction-of-founder/blob/main/职场言情/0_日志/创作日志1.md>

**用途**:演示 `material` 命令的完整工作流。原始文件见 [`fiction-of-founder/创作日志1.md`](fiction-of-founder/创作日志1.md)(一篇关于《职场言情》小说创作动机、潜意识与叙事疗法的创作谈)。

## 四个命令 · 四个阶段

| 阶段 | 命令 | 语义 | 产物 |
|------|------|------|------|
| **收集** | `material collect [--url]` | 从文本或链接获得内容,条目化 + YAML 标注为**初步加工版本** | `journal/YYYY-MM-DD.md` |
| **整理** | `material organize` | LLM 根据主题分组和标记(写入日志 YAML 归属,保留人工标注) | 日志 front matter |
| **提取** | `material distill <主题>` | 聚合条目 → LLM **删除次要信息**(过程性叙述、用途信息、重复、情绪宣泄)→ 组织稿 | `materials/<主题>.md` |
| **表达** | `material express <主题>` | 基于组织稿生成**初稿**(自动判断写作意图) | `materials/<主题>-初稿.md` |
| | `material express <主题> --goal <目标>` | 基于初稿生成**定稿**(按写作目标) | `materials/<主题>-定稿.md` |

产物链:收集(01)→ 组织(03)→ 初稿(04)→ 定稿(05)。

## 工作流演示

```sh
# 1. 收集 — 从链接获得文件
material collect --url "https://raw.githubusercontent.com/quanttide/quanttide-fiction-of-founder/main/职场言情/0_日志/创作日志1.md" --title 创作日志1

# 2. 整理 — 根据主题分组和标记(需 DEEPSEEK_API_KEY)
material organize
# → 日志 YAML front matter 写入归属:
#   ---
#   topics:
#     "创作日志1": 创作动机

# 3. 提取 — 删除次要信息(通用判据:过程叙述/用途信息/重复/情绪宣泄)
material distill 创作动机
# → materials/创作动机.md(组织稿)

# 4. 表达 — 初稿(自动判断写作意图)与定稿(按目标)
material express 创作动机
# → materials/创作动机-初稿.md
material express 创作动机 --goal "写一篇用于公司账号发布的品牌故事"
# → materials/创作动机-定稿.md
```

## 案例产物(实测归档)

| 文件 | 生成命令 | 说明 |
|------|----------|------|
| [`01-journal-收集.md`](fiction-of-founder/01-journal-收集.md) | `collect --url` + `organize` | 收集的初步加工版本:日志条目 + YAML 归属 |
| [`03-distill-组织.md`](fiction-of-founder/03-distill-组织.md) | `distill 创作动机` | 组织稿:结构化要点,次要信息已删除(无用途/渠道类残留) |
| [`04-express-初稿.md`](fiction-of-founder/04-express-初稿.md) | `express 创作动机` | 初稿:自动判断写作意图 → 第一人称创作谈 |
| [`05-express-定稿.md`](fiction-of-founder/05-express-定稿.md) | `express 创作动机 --goal "写一篇用于公司账号发布的品牌故事"` | 定稿:按目标基于初稿生成品牌故事 |

> 环境变量 `DEEPSEEK_API_KEY` 由 `organize`/`distill`/`express` 读取(经 quanttide-agent 调 DeepSeek);`collect` 为纯本地操作。
