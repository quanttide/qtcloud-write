#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== 写作云 — 安装依赖 ==="

# ── Provider ──────────────────────────────────────────────
echo ""
echo "[1/3] Python 依赖（provider）"
cd "$ROOT/src/provider"
if command -v uv &>/dev/null && uv pip install -e . 2>/dev/null; then
    :
elif command -v pip &>/dev/null; then
    pip install -e .
else
    echo "未找到 pip 或 uv，请先安装 Python ≥ 3.11"
    exit 1
fi

if [ ! -f .env ]; then
    cp .env.example .env
    echo "已创建 .env，请填入 DEEPSEEK_API_KEY"
fi

# ── Studio ────────────────────────────────────────────────
echo ""
echo "[2/3] Flutter 依赖（studio）"
cd "$ROOT/src/studio"
if command -v flutter &>/dev/null; then
    flutter pub get
else
    echo "未找到 flutter，请先安装 Flutter SDK"
    exit 1
fi

# ── 验证 ──────────────────────────────────────────────────
echo ""
echo "[3/3] 验证"
cd "$ROOT/src/provider"
python -m pytest tests/ -q --tb=short 2>/dev/null && echo "  provider 测试通过" || echo "  provider: 跳过测试（需 .env 配置）"

cd "$ROOT/src/studio"
flutter test --quiet 2>/dev/null && echo "  studio 测试通过" || echo "  studio: 测试失败"

echo ""
echo "=== 安装完成 ==="
echo ""
echo "启动 provider:  cd src/provider && uvicorn app.main:app --port 9000"
echo "启动 studio:    cd src/studio && flutter run -d chrome --dart-define=PROVIDER_URL=http://localhost:9000"
