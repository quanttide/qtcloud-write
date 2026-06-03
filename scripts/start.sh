#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "启动 provider..."
cd "$ROOT/src/provider" && uvicorn app.main:app --port 9000 &
PID=$!
sleep 2
echo "启动 studio..."
"$ROOT/src/studio/build/linux/x64/release/bundle/qtcloud_write_studio" &
wait $PID
