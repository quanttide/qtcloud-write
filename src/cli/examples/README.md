# 案例:创始人小说创作日志

**数据来源**:[quanttide/quanttide-fiction-of-founder](https://github.com/quanttide/quanttide-fiction-of-founder)《职场言情》创作日志 1

<https://github.com/quanttide/quanttide-fiction-of-founder/blob/main/职场言情/0_日志/创作日志1.md>

**用途**:演示 `material` 命令的完整工作流。原始文件见 [`fiction-of-founder/创作日志1.md`](fiction-of-founder/创作日志1.md)(一篇关于《职场言情》小说创作动机、潜意识与叙事疗法的创作谈)。

## 四个命令 · 四个阶段 · 四个产物

| 阶段 | 命令 | 语义 | 产物 |
|------|------|------|------|
| **01 收集** | `material collect [--url]` | 从文本或链接获得内容,条目化 + YAML 标注为**初步加工版本** | `journal/YYYY-MM-DD.md` |
| **02 分组** | `material organize` | LLM 根据主题**分组和标记**(YAML 归属),并生成**分组文件** | `groups/<主题>.md` |
| **03 初稿** | `material distill <主题>` | 读分组 → **过滤次要信息 + 统一表达**形成初稿 | `materials/<主题>.md` |
| **04 定稿** | `material express <主题> [--goal]` | 参考分组素材,根据写作目标形成定稿(缺省自动判断意图) | `materials/<主题>-定稿.md` |

## 工作流演示

```sh
# 1. 收集 — 从链接获得文件
material collect --url "https://raw.githubusercontent.com/quanttide/quanttide-fiction-of-founder/main/职场言情/0_日志/创作日志1.md" --title 创作日志1

# 2. 分组 — 根据主题分组和标记(需 DEEPSEEK_API_KEY)
material organize
# → 日志 YAML front matter 写入归属,并生成分组文件:
#   groups/创作心路.md(该主题下的条目原文聚合)

# 3. 初稿 — 过滤次要信息 + 统一表达
material distill 创作心路
# → materials/创作心路.md(连贯初稿,无用途/渠道类信息残留)

# 4. 定稿 — 参考分组素材,根据写作目标形成定稿
material express 创作心路                                    # 自动判断意图
material express 创作心路 --goal "写一篇用于公司账号发布的品牌故事"  # 指定目标
# → materials/创作心路-定稿.md
```

## 案例产物(实测归档)

| 文件 | 生成命令 | 说明 |
|------|----------|------|
| [`01-journal-收集.md`](fiction-of-founder/01-journal-收集.md) | `collect --url` | 收集的初步加工版本:日志条目 |
| [`02-organize-分组.md`](fiction-of-founder/02-organize-分组.md) | `organize` | 分组:主题归属 + 条目原文聚合(`groups/<主题>.md`) |
| [`03-distill-初稿.md`](fiction-of-founder/03-distill-初稿.md) | `distill 创作心路` | 初稿:过滤次要信息 + 统一表达,连贯成篇 |
| [`04-express-定稿.md`](fiction-of-founder/04-express-定稿.md) | `express 创作心路 --goal "写一篇用于公司账号发布的品牌故事"` | 定稿:参考分组素材,按写作目标 |

> 环境变量 `DEEPSEEK_API_KEY` 由 `organize`/`distill`/`express` 读取(经 quanttide-agent 调 DeepSeek);`collect` 为纯本地操作。
