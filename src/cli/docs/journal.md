# journal.rs — 日志:收集与条目

## 职责

实现产物链的 **01 收集**:把想法(文本或链接)追加为日志条目;并提供条目解析、front matter 更新、按主题收集条目等下游模块依赖的基础能力。

## 存储布局与格式

```
<workdir>/journal/YYYY-MM-DD.md
```

```markdown
## 09:30
宣传册的创始人职责区分,逻辑还不够严谨

## 09:30-2
同一分钟的第二条想法(标题带序号)
```

- **按日期分文件**:一天一个 markdown 文件,对齐 `data/journal` 子模块的既有惯例,天然可排序、可 git 回溯。
- **条目 = `## 标题` 小节**:标题默认是时间戳 `HH:MM`;条目 id 由标题直接生成(`:` → `-`),因此**删除中间条目不会导致其他条目 id 漂移**(YAML 标注不会错位)。

## 核心函数

| 函数 | 说明 |
|------|------|
| `collect(workdir, text)` | 追加一条想法,标题为当前时间;同分钟多条自动 `HH:MM-2` 序号 |
| `collect_from_url(workdir, url, title)` | 从链接下载内容作为条目;标题默认取 URL 文件名 |
| `read_entries(body)` | 解析正文为 `Entry` 列表(`file`/`id`/`title`/`text`) |
| `read_all(workdir)` | 读全部日志文件,返回 `JournalFile`(文件名 + front matter + 条目) |
| `update_front_matter(workdir, file, f)` | 读 → 闭包修改 front matter → 写回(organize 用) |
| `collect_for_topic(workdir, topic)` | 按 YAML 归属收集某主题的全部条目(organize 分组用) |

## 设计思路

1. **标题即 id,id 即引用**:`Entry::reference()` 返回 `2026-08-15.md#09-30`,这是跨文件引用的统一格式——分组文件的 `sources`、素材文件的来源标注都用它。标题文本是 id 的唯一来源,保证幂等。
2. **append-only 收集**:`collect` 只追加、永不改写已有内容(只补空行分隔),尊重"随时随地记录"的低摩擦诉求,也保证 git 历史干净。
3. **同分钟序号写进标题**(`## 09:30-2` 而非依赖解析时计数):id 稳定基于文件内容,而不是"第几次出现"——后者在删除条目后会重排 id。
4. **front matter 与正文分离维护**:`collect` 不碰 front matter(收集期无主题概念);`organize` 通过 `update_front_matter` 注入标注。职责边界清晰。
5. **网络下载走代理**:`collect_from_url` 从环境变量读取 `https_proxy`/`http_proxy`/`all_proxy`(仅 http(s) 代理)配置 ureq,并设置连接/总超时。没有这一步,在代理环境下直连 GitHub 会挂起(实测踩坑:curl 正常而 ureq 超时,因为 ureq 默认不读环境代理)。
