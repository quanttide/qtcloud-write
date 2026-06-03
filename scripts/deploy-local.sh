#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== 写作云 — 本地部署 ==="
echo ""

# ── 前置检查 ────────────────────────────────────────────
check() { command -v "$1" &>/dev/null || { echo "需要 $1"; exit 1; }; }
check python3
check flutter
echo "  Python  $(python3 --version 2>&1 | cut -d' ' -f2)"
echo "  Flutter $(flutter --version 2>&1 | head -1 | cut -d' ' -f2)"
echo ""

# ── Provider ─────────────────────────────────────────────
echo "--- provider ---"
cd "$ROOT/src/provider"
command -v uv &>/dev/null && uv pip install -e . 2>/dev/null || pip install -e .
if [ ! -f .env ]; then cp .env.example .env; fi
if grep -q "your_deepseek_api_key_here" .env 2>/dev/null; then
    echo "  DeepSeek API Key（可留空跳过）"
    read -r -p "  Key: " k
    [ -n "$k" ] && sed -i "s/your_deepseek_api_key_here/$k/" .env
fi
echo ""

# ── Studio ───────────────────────────────────────────────
echo "--- studio ---"
cd "$ROOT/src/studio"
flutter pub get >/dev/null 2>&1
flutter build linux --release >/dev/null 2>&1
echo "  构建完成"
echo ""

# ── 启动 ─────────────────────────────────────────────────
echo "--- 启动 ---"
cd "$ROOT/src/provider"
echo "  provider  http://localhost:9000"
uvicorn app.main:app --port 9000 &
PROVIDER_PID=$!
sleep 2

"$ROOT/src/studio/build/linux/x64/release/bundle/qtcloud_write_studio" &
STUDIO_PID=$!

echo ""
echo "  按 Ctrl+C 停止所有服务"
trap "kill $PROVIDER_PID $STUDIO_PID 2>/dev/null" EXIT
wait
