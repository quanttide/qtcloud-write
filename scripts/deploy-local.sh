#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== 写作云 — 本地安装 ==="
echo ""

# ── 前置检查 ────────────────────────────────────────────
if ! python3 --version 2>/dev/null | grep -qE "^Python 3\.(1[1-9]|[2-9][0-9])"; then
    echo "需要 Python ≥ 3.11"
    exit 1
fi
echo "  Python  $(python3 --version 2>&1 | cut -d' ' -f2)"

if ! flutter --version 2>/dev/null | grep -q "Flutter"; then
    echo "需要 Flutter SDK"
    exit 1
fi
echo "  Flutter $(flutter --version 2>&1 | head -1 | cut -d' ' -f2)"
echo ""

# ── Provider ─────────────────────────────────────────────
echo "--- 安装 provider ---"
cd "$ROOT/src/provider"

if command -v uv &>/dev/null && uv pip install -e . 2>/dev/null; then
    :
else
    pip install -e .
fi
echo "  Python 依赖已安装"

if [ ! -f .env ]; then
    cp .env.example .env
fi
if grep -q "your_deepseek_api_key_here" .env 2>/dev/null; then
    echo ""
    echo "  配置 DeepSeek API Key（深度分析需要，可留空跳过）"
    read -r -p "  API Key: " INPUT_KEY
    if [ -n "$INPUT_KEY" ]; then
        sed -i "s/your_deepseek_api_key_here/$INPUT_KEY/" .env
        echo "  已写入 .env"
    else
        echo "  跳过，本地分析功能可用"
    fi
fi
echo ""

# ── Studio ───────────────────────────────────────────────
echo "--- 安装 studio ---"
cd "$ROOT/src/studio"
flutter pub get
echo "  Flutter 依赖已安装"
echo ""

# ── 启动指引 ────────────────────────────────────────────
echo "--- 启动 ---"
echo ""
echo "  终端 1 — 启动后端:"
echo "    cd src/provider && uvicorn app.main:app --port 9000 --reload"
echo ""
echo "  终端 2 — 启动前端:"
echo "    cd src/studio && flutter run -d chrome --dart-define=PROVIDER_URL=http://localhost:9000"
echo ""
