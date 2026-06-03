#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== 写作云 — 本地部署 ==="
echo ""

# ── 前置检查 ────────────────────────────────────────────
check() {
    if ! command -v "$1" &>/dev/null; then
        echo "需要 $1，请先安装"
        exit 1
    fi
}
check python3
check flutter
echo "  Python  $(python3 --version 2>&1 | cut -d' ' -f2)"
echo "  Flutter $(flutter --version 2>&1 | head -1 | cut -d' ' -f2)"
echo ""

# ── Provider ─────────────────────────────────────────────
echo "--- provider ---"
cd "$ROOT/src/provider"
if command -v uv &>/dev/null && uv pip install -e . 2>/dev/null; then
    :; else pip install -e .
fi
if [ ! -f .env ]; then
    cp .env.example .env
fi
if grep -q "your_deepseek_api_key_here" .env 2>/dev/null; then
    echo "  DeepSeek API Key（可留空跳过）"
    read -r -p "  Key: " k
    [ -n "$k" ] && sed -i "s/your_deepseek_api_key_here/$k/" .env
fi
echo "  OK"
echo ""

# ── Studio ───────────────────────────────────────────────
echo "--- studio ---"
cd "$ROOT/src/studio"
flutter pub get >/dev/null 2>&1
flutter build linux --release >/dev/null 2>&1
echo "  构建完成: src/studio/build/linux/x64/release/bundle/qtcloud_write_studio"
echo ""

# ── 启动脚本 ────────────────────────────────────────────
cat > "$ROOT/start.sh" << 'SCRIPT'
#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "启动 provider..."
cd "$ROOT/src/provider" && uvicorn app.main:app --port 9000 &
PID=$!
sleep 2
echo "启动 studio..."
"$ROOT/src/studio/build/linux/x64/release/bundle/qtcloud_write_studio" &
wait $PID
SCRIPT
chmod +x "$ROOT/start.sh"
echo "--- 完成 ---"
echo ""
echo "  运行 ./start.sh 一键启动"
echo "  或分两个终端启动："
echo "    provider:  cd src/provider && uvicorn app.main:app --port 9000"
echo "    studio:    src/studio/build/linux/x64/release/bundle/qtcloud_write_studio"
echo ""
