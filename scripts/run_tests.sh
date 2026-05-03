#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "── Provider unit tests ──────────────────────────────────────"
uv run pytest "$ROOT/src/provider/tests/" -v

echo ""
echo "── Flutter analyze ──────────────────────────────────────────"
cd "$ROOT/src/studio" && flutter analyze

echo ""
echo "── Integration tests ────────────────────────────────────────"
uv run pytest "$ROOT/tests/" -v
