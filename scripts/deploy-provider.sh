#!/usr/bin/env bash
# 构建并部署 qtcloud-write-provider 到阿里云 FaaS

set -euo pipefall

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROVIDER_DIR="$PROJECT_ROOT/src/provider"
IMAGE_NAME="qtcloud-write-provider"
REGISTRY="crpi-uorshhk4a32pmmio.cn-hangzhou.personal.cr.aliyuncs.com"

echo "=== 1. 构建 Docker 镜像 ==="
cd "$PROVIDER_DIR"
docker build -t "$IMAGE_NAME:latest" .

echo ""
echo "=== 2. 推送到阿里云容器镜像服务 ==="
docker tag "$IMAGE_NAME:latest" "$REGISTRY/quanttide/$IMAGE_NAME:latest"
docker push "$REGISTRY/quanttide/$IMAGE_NAME:latest"

echo ""
echo "=== 完成 ==="
echo "镜像已推送，请登录阿里云函数计算控制台创建函数"
echo "镜像地址: $REGISTRY/quanttide/$IMAGE_NAME:latest"
