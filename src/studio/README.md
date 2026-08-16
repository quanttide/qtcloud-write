# 写作云 Studio

写作云 AI 原生写作编辑器（qtcloud-write 的桌面端写作工作台）。

核心原则：**AI 只产出结构（元数据），绝不改写原文**——分析结果存于 `.analysis/` 目录，
删除即完全还原；标注是视图，不是内容。

## 快速启动

```bash
# Linux 桌面（推荐）
DEEPSEEK_API_KEY=sk-xxx flutter run -d linux

# Web
flutter run -d chrome
```

数据源默认指向 qtcloud-write CLI 的示例工作目录
（`src/cli/examples/fiction-of-founder`，含 `journal/ groups/ materials/` 四命令产物），
可用 `--dart-define=QTCLOUD_WRITE_DATA_PATH=/path/to/workdir` 覆盖。

## 工作流（对齐 CLI 四命令）

客户端在左侧导航底部提供**流程操作面板**，直接复现 CLI 四命令（共享同一数据目录）：

| 步骤 | 客户端操作 | CLI 对应 | 产物 |
|------|-----------|----------|------|
| 01 收集 | 输入想法 → 收集 | `material collect` | `journal/YYYY-MM-DD.md`（`## HH:MM` 条目） |
| 02 分组 | LLM 分组 | `material organize` | 日志 YAML 归属 + `groups/<主题>.md` |
| 03 初稿 | 选中 02_分组 章节 → 生成初稿 | `material distill` | `materials/<主题>.md` |
| 04 定稿 | 选中 03_初稿 章节 → 生成定稿 | `material express` | `materials/<主题>-定稿.md` |

核心原则：**AI 只产出结构（元数据），绝不改写原文**——分析结果存于 `.analysis/` 目录，
删除即完全还原；标注是视图，不是内容。工作流产物为 git 管理的 Markdown。

## 测试

```bash
flutter test
```

## 项目结构

```
lib/
├── main.dart                        # 入口（写作编辑器直入）
├── config.dart                      # 数据源 / LLM 配置
├── blocs/
│   ├── app_bloc_provider.dart       # 应用级 Bloc Provider
│   ├── workflow/workflow_bloc.dart  # 四阶段工作流
│   ├── editor/editor_bloc.dart      # 编辑器状态（自动保存/字数/脏标记）
│   └── analyze/analyze_bloc.dart    # AI 整理（缓存/负反馈/采纳灵感）
├── models/
│   ├── chapter.dart                 # 章节
│   ├── workflow.dart                # 阶段模型
│   └── analysis.dart                # 整理层（元数据，零改写）
├── repositories/
│   ├── chapter_repository.dart      # 章节数据抽象
│   ├── file_chapter_repository.dart # 文件实现（CLI 目录映射）
│   └── analysis_repository.dart     # .analysis/ 缓存
├── services/
│   └── llm_client.dart              # DeepSeek API（DEEPSEEK_API_KEY，环境代理）
├── workflow/                        # CLI 四命令的 Dart 移植（客户端复现）
│   ├── frontmatter.dart             # YAML front matter 解析/渲染
│   ├── journal.dart                 # collect 记录 + 条目解析
│   ├── organize.dart                # LLM 主题分组 + groups/ 生成
│   ├── distill.dart                 # 过滤杂质 + 成文 → 初稿
│   └── express.dart                 # 按目标重构 → 定稿
├── widgets/
│   └── workflow_actions_panel.dart  # 流程操作面板（四命令入口）
└── screens/
    ├── create_screen_new.dart       # 三栏编辑器（章节树 + 编辑区 + AI 面板）
    ├── annotation_overlay.dart      # 只读标注层（拆分线/场景色条）
    └── analysis_panel.dart          # AI 整理面板
```
