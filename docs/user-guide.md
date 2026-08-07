# User Guide

写作云是一个面向叙事写作的 AI 辅助分析工具。它由两个组件组成：

- **Provider**（后端 API）— 基于 DeepSeek 的叙事分析服务
- **Studio**（桌面客户端）— Linux 桌面应用，提供编辑器 + 分析面板

## 前置要求

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| Python | ≥ 3.11 | 运行 Provider |
| Flutter | ≥ 3.0 | 构建 Studio |
| DeepSeek API Key | 有效密钥 | AI 分析能力（可选，无 key 时仅本地分析可用） |

## 安装

```bash
# 克隆仓库
git clone https://github.com/quanttide/quanttide-write.git
cd quanttide-write/apps/qtcloud-write

# 一键部署
bash scripts/deploy-local.sh
```

`deploy-local.sh` 会自动完成：

1. 安装 Provider Python 依赖
2. 构建 Studio Linux 桌面客户端
3. 启动 Provider（端口 9000）和 Studio

## 配置 DeepSeek API Key

AI 分析需要 DeepSeek API Key。设置环境变量后启动 Provider：

```bash
export DEEPSEEK_API_KEY="sk-你的密钥"
bash scripts/deploy-local.sh
```

未配置 API Key 时，评审功能可用但结果是本地离线分析，非 AI 生成。

## 使用 Studio

### 界面布局

```
┌─────────────────────────────────────────────────────┐
│  ✎ 写作云 合成工作台     [▶ 评审] [加载样本]        │  顶栏
├────────┬────────────────────────┬──────────────────┤
│ 📄 底稿 │  编辑器                │  Review  ✓        │
│        │  (输入或粘贴文本)       │  评分             │
│ 咖啡厅  │                        │                   │
│ 重逢    │                        │  📋 评审 🎯 情境  │
│        │                        │  ✏️ 改写           │
│        │                        │                   │
│        │                        │  分析结果          │
├────────┴────────────────────────┴──────────────────┤
│  字数 412                  AI分析                   │  底栏
└─────────────────────────────────────────────────────┘
```

### 基本操作

**1. 加载样本**

点击顶栏「加载样本」按钮，编辑器会填入示例文章并自动运行评审。适合快速体验。

**2. 输入或粘贴文本**

直接在编辑器区域输入你自己的文章。

**3. 运行评审**

点击「▶ 评审」按钮：

- Provider 可用时 → AI 分析，结果展示在右侧面板
- Provider 不可用时 → 本地离线分析（底部状态栏显示"本地分析"）

**4. 查看评审结果**

右侧面板按三个标签页组织：

- **📋 评审** — 整体分析结论、段落结构标注、改进建议
- **🎯 情境** — 叙事空隙诊断（需 Provider 支持）
- **✏️ 改写** — 具体改写建议

**5. 编辑 / 预览切换**

工具栏右侧的「编辑」/「预览」按钮切换 Markdown 编辑模式和渲染预览模式。

### 状态栏指示

底部状态栏显示：

- 字数统计
- 当前分析模式：`AI分析`（连接 Provider）或 `本地分析`（离线模式）

## 使用 Provider API

Provider 提供 REST API，可直接用 `curl` 调用。

### 评审文章

```bash
curl -X POST http://localhost:9000/review \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的文章",
    "paragraphs": ["第一段内容", "第二段内容"],
    "author": "me",
    "tag": "bad"
  }'
```

### 空隙诊断

```bash
curl -X POST http://localhost:9000/reflect \
  -H "Content-Type: application/json" \
  -d '{"text": "他推开门走了出去。第二天，她又来了。"}'
```

### 全文改写

```bash
curl -X POST http://localhost:9000/rewrite \
  -H "Content-Type: application/json" \
  -d '{"text": "他推开门走了出去。"}'
```

### 完整 3R 流程

```bash
curl -X POST http://localhost:9000/cycle \
  -H "Content-Type: application/json" \
  -d '{"text": "他推开门走了出去。第二天，她又来了。"}'
```

### 积累风格样本

将 `tag` 设为 `good` 提交文章，Provider 会将其存入风格库用于后续对比：

```bash
curl -X POST http://localhost:9000/review \
  -H "Content-Type: application/json" \
  -d '{
    "title": "优秀范文",
    "paragraphs": ["以个人困境出发的文章..."],
    "author": "expert",
    "tag": "good"
  }'
```

## 数据存储

Provider 将数据存储在 `src/provider/data/` 目录：

| 文件 | 内容 |
|------|------|
| `store.db` | SQLite 数据库，存储风格样本（好文章） |
| `provider.log` | 运行时日志，按天轮转保留 7 天 |

## 日志

Provider 日志写入 `src/provider/data/provider.log`。调试时可查看：

```bash
tail -f src/provider/data/provider.log
```

## 常见问题

**评审按钮点了没反应？**

确认 Provider 是否正在运行。如果 Provider 未启动，评审会走离线模式，结果可能不准确。

**状态栏显示"本地分析"而不是"AI分析"？**

表示未检测到 Provider 或 Provider 未配置 API Key。设置 `DEEPSEEK_API_KEY` 环境变量后重启。

**API 返回 502 Bad Gateway？**

Provider 调用 DeepSeek 失败。检查：

1. API Key 是否正确设置
2. 网络是否能访问 `api.deepseek.com`
3. Provider 日志中的详细错误信息
