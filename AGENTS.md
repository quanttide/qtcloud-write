# AGENTS.md - qtcloud-write

## 文档地图

| 文档 | 认知角色 | 内容概要 |
|------|----------|----------|
| [README.md](README.md) | 用户 | 快速开始、命令参考 |
| [CHANGELOG.md](CHANGELOG.md) | 用户 | 版本变更记录 |
| [STATUS.md](STATUS.md) | 用户 | 项目总览与子项目概括 |
| [AGENTS.md](AGENTS.md) | 内部 | 开发心智模型与执行约束 |

> 设计文档（BRD/PRD/PMD/QA/IXD/ADD）已迁移至 [docs/vision/platform](https://github.com/quanttide/quanttide-vision-of-narrative-engineering)。

## 执行约束

发布 Release 时，必须加载主仓库 `devops-release` Skill 并按工作流**逐行执行**，不可跳过预检查。子模块有独立 CHANGELOG（`src/provider/CHANGELOG.md`、`src/studio/CHANGELOG.md`），对应各自 tag（`provider/v*`、`studio/v*`），发布时分别检查。

## 思考方式

### 演化路径

写作云从叙事工程信息共享为起点，提供分析结果和风格积累；再逐渐向具体写作活动延伸，逐渐加入常见的写作工具。

### 经验教训

**产品层面**：每次方向错位都是因为从实现路径倒推产品定位（"有分析能力了，做个改写界面吧"），而不是从用户困境倒推。

**文档层面**：同样的模式会转移到写文档上——AI 容易把"当前不做的选择"固化为"不可逾越的规则"，把优先级问题写成约束问题。应写成"从这里起步、往那里延伸"，而非"绝不做什么"。

## 执行约束

### PMD 承载方向

方向文档已合并到 PMD。PMD 既承载"做过什么、待验证方向"，也承接原 ROADMAP 的减负职责——让人不需要问"接下来呢"。

**PMD 的方向部分结构：**
- **目标**：一句话说明当前要验证什么
- **行动**：checkbox 列表，每项动作用 `—` 行内说明意图
- **回顾**：已完成项用 `✓` 标记，自然翻篇
