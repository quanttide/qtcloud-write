#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROVIDER_DIR="$PROJECT_ROOT/src/provider"
IMAGE_NAME="qtcloud-write-provider"
REGISTRY="crpi-uorshhk4a32pmmio.cn-hangzhou.personal.cr.aliyuncs.com"
REMOTE_IMAGE="$REGISTRY/quanttide/$IMAGE_NAME:latest"

echo "=== 1. Build linux/amd64 Docker image ==="
cd "$PROVIDER_DIR"
docker buildx inspect qtcloud-write-builder >/dev/null 2>&1 || \
  docker buildx create --name qtcloud-write-builder --use
docker buildx build \
  --platform linux/amd64 \
  --provenance=false \
  --sbom=false \
  -t "$IMAGE_NAME:latest" \
  --load \
  .

echo ""
echo "=== 2. Push to Alibaba Cloud Container Registry ==="
docker tag "$IMAGE_NAME:latest" "$REMOTE_IMAGE"
docker push "$REMOTE_IMAGE"

echo ""
echo "=== Done ==="
echo "Image pushed: $REMOTE_IMAGE"
