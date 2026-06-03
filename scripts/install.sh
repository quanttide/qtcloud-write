#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

pass() { echo -e "  ${GREEN}✓${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }
info() { echo -e "  ${CYAN}→${NC} $1"; }

echo "=== 写作云 — 本地安装 ==="
echo ""

# ── 前置检查 ────────────────────────────────────────────
echo "--- 检查环境 ---"

PY_OK=0
if python3 --version 2>/dev/null | grep -qE "^Python 3\.(1[1-9]|[2-9][0-9])"; then
    pass "Python $(python3 --version 2>&1 | cut -d' ' -f2)"
    PY_OK=1
else
    fail "需要 Python ≥ 3.11"
fi

FL_OK=0
if flutter --version 2>/dev/null | grep -q "Flutter"; then
    pass "Flutter $(flutter --version 2>&1 | head -1 | cut -d' ' -f2)"
    FL_OK=1
else
    fail "需要 Flutter SDK"
fi

if [ "$PY_OK$FL_OK" = "00" ]; then
    echo "请先安装 Python 3.11+ 和 Flutter SDK"
    exit 1
fi
echo ""

# ── Provider ─────────────────────────────────────────────
echo "--- 安装 provider ---"
cd "$ROOT/src/provider"

if [ "$PY_OK" = 1 ]; then
    if command -v uv &>/dev/null && uv pip install -e . 2>/dev/null; then
        pass "provider Python 依赖"
    elif pip install -e . 2>/dev/null; then
        pass "provider Python 依赖"
    else
        fail "provider 依赖安装失败"
    fi

    # 配置 API Key
    if [ ! -f .env ]; then
        cp .env.example .env
        info "已创建 .env"
    fi
    if grep -q "your_deepseek_api_key_here" .env 2>/dev/null; then
        echo ""
        echo "  DeepSeek API Key 未配置。有两种方式："
        echo "    1) 编辑 src/provider/.env，填入你的 key"
        echo "    2) 无 key 也能启动（本地分析功能正常，深度分析不可用）"
        echo ""
        read -r -p "  现在输入 key（留空跳过）: " INPUT_KEY
        if [ -n "$INPUT_KEY" ]; then
            sed -i "s/your_deepseek_api_key_here/$INPUT_KEY/" .env
            pass "API Key 已写入 .env"
        else
            info "跳过 API Key 配置"
        fi
    fi
fi
echo ""

# ── Studio ───────────────────────────────────────────────
echo "--- 安装 studio ---"
cd "$ROOT/src/studio"

if [ "$FL_OK" = 1 ]; then
    flutter pub get --quiet 2>/dev/null && pass "studio Flutter 依赖" || fail "flutter pub get 失败"
fi
echo ""

# ── 验证 ─────────────────────────────────────────────────
echo "--- 验证 ---"

cd "$ROOT/src/provider"
if python -m pytest tests/ -q --tb=short 2>&1 | tail -1 | grep -q "passed"; then
    pass "provider 测试通过"
else
    fail "provider 测试未通过"
fi

cd "$ROOT/src/studio"
if flutter test --quiet 2>&1 | tail -1 | grep -q "All tests passed"; then
    pass "studio 测试通过"
else
    fail "studio 测试未通过"
fi
echo ""

# ── 启动 ─────────────────────────────────────────────────
echo "--- 启动 ---"
echo ""
echo "  终端 1 — 启动后端:"
echo "    cd $ROOT/src/provider"
echo "    uvicorn app.main:app --port 9000 --reload"
echo ""
echo "  终端 2 — 启动前端:"
echo "    cd $ROOT/src/studio"
echo "    flutter run -d chrome --dart-define=PROVIDER_URL=http://localhost:9000"
echo ""
echo "  浏览器打开 Flutter 窗口 → 点击「🧠 深度分析」体验完整 3R 流程"
echo ""
