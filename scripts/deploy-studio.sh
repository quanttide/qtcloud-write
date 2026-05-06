#!/usr/bin/env bash
# 构建 Flutter Web 并上传到 OSS

set -euo pipefall

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STUDIO_DIR="$PROJECT_ROOT/src/studio"

echo "=== 1. 构建 Flutter Web ==="
cd "$STUDIO_DIR"
flutter build web --release

echo ""
echo "=== 2. 上传到 OSS ==="
python3 "$SCRIPT_DIR/upload-studio-oss.py"

echo ""
echo "=== 完成 ==="
echo "访问: https://qtcloud-write-studio.oss-cn-hangzhou.aliyuncs.com"
