# main.rs — CLI 入口与命令分发

## 职责

定义 `material` 命令的四子命令结构(clap derive),并把每个命令分发到对应模块。**不包含业务逻辑**,只做参数解析、工作目录确定与错误出口。

## 命令结构

```rust
enum Commands {
    Collect { text: Option<String>, url: Option<String>, title: Option<String> },
    Organize,
    Distill { topic: String },
    Express { topic: String, goal: Option<String> },
}
```

- `collect`:`text`(想法文本)与 `--url`(链接)二选一,`--title` 可选覆盖条目标题
- `organize`:无参数
- `distill <主题>`:一个位置参数
- `express <主题> [--goal 写作目标]`:`--goal` 缺省时由 LLM 自动判断写作意图

## 设计思路

1. **四命令四阶段一一对应**:`collect`/`organize`/`distill`/`express` 直接对应产物链 01/02/03/04,命令名即阶段名,没有多余的子命令层级。
2. **工作目录即操作范围**:`workdir = std::env::current_dir()`,所有产物(`journal/`、`groups/`、`materials/`)都落在当前目录下——把当前目录当作一个"写作工作区",配合 git 管理历史。
3. **错误出口统一**:所有命令返回 `Result<(), String>`,`main` 统一打印 `错误:{e}` 并以 exit 1 退出;成功信息由各命令自行打印(产物路径是主要输出)。

## 与模块的关系

```
main.rs ──> journal::collect / collect_from_url     (01 收集)
main.rs ──> organize::organize + write_groups       (02 分组)
main.rs ──> distill::distill                        (03 初稿)
main.rs ──> express::express                        (04 定稿)
```

`main` 不知道"怎么做",只负责"让谁做"。后续新增命令(如 `list`、`import`)时,只需在 `Commands` 增加变体并接一条分发分支。
