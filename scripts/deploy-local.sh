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
echo "  已安装。设置 DEEPSEEK_API_KEY 环境变量以启用 AI 分析"

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
