# 案例:创始人小说创作日志

**数据来源**:[quanttide/quanttide-fiction-of-founder](https://github.com/quanttide/quanttide-fiction-of-founder)《职场言情》创作日志 1

<https://github.com/quanttide/quanttide-fiction-of-founder/blob/main/职场言情/0_日志/创作日志1.md>

**用途**:演示 `material` 命令的完整 CODE 工作流。原始文件见 [`fiction-of-founder/创作日志1.md`](fiction-of-founder/创作日志1.md)(一篇关于《职场言情》小说创作动机、潜意识与叙事疗法的创作谈)。

## CODE 语义

| 阶段 | 命令 | 语义 |
|------|------|------|
| **C**ollect | `material collect` | 收集:从文本或**链接**获得内容,追加到日志 |
| **O**rganize | `material organize` | 整理:根据主题分组和标记(LLM 提取 → 日志 YAML 归属,保留人工标注) |
| **D**istill | `material distill [--refine]` | 提取:按主题聚合条目;`--refine` 删除次要信息 |
| **E**xpress | `material express [--goal]` | 表达:根据写作目标判断;缺省**自动根据内容判断写作意图** |

## 工作流演示

```sh
# 1. 收集 — 从链接获得文件
material collect --url "https://raw.githubusercontent.com/quanttide/quanttide-fiction-of-founder/main/职场言情/0_日志/创作日志1.md" --title 创作日志1

# 2. 整理 — 根据主题分组和标记(需 DEEPSEEK_API_KEY)
material organize
# → journal/YYYY-MM-DD.md 的 YAML front matter 写入条目归属:
#   ---
#   topics:
#     "创作日志1": 创作动机

# 3. 提取 — 删除次要信息
material distill 创作动机            # 聚合 → materials/创作动机.md
material distill 创作动机 --refine   # 提炼 → materials/创作动机-refined.md

# 4. 表达 — 根据写作目标判断(默认自动判断写作意图)
material express 创作动机                                   # 自动判断意图 → materials/创作动机-成稿.md
material express 创作动机 --goal "写一篇品牌故事"             # 指定写作目标
```

## 产物结构

```
<workdir>/
├── journal/
│   └── YYYY-MM-DD.md        # 日志:## 条目 + YAML 归属(front matter)
└── materials/
    ├── 创作动机.md           # distill 聚合稿
    ├── 创作动机-refined.md   # distill --refine 提炼稿(删除次要信息)
    └── 创作动机-成稿.md       # express 成稿
```

> 环境变量 `DEEPSEEK_API_KEY` 由 `organize`/`distill --refine`/`express` 读取(经 quanttide-agent 调 DeepSeek);`collect`/`distill`(聚合)为纯本地操作。
