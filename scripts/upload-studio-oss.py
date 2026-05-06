#!/usr/bin/env python3
"""上传 qtcloud-write Flutter Web 构建产物到阿里云 OSS"""

import oss2
import os
from pathlib import Path

# 阿里云配置
ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID", "")
ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET", "")
BUCKET_NAME = "qtcloud-write"
REGION = "cn-hangzhou"
ENDPOINT = f"oss-{REGION}.aliyuncs.com"

# 本地 build 目录
BUILD_DIR = Path(__file__).parent.parent / "src" / "studio" / "build" / "web"


def upload_file(bucket, local_path: Path, remote_path: str):
    """上传单个文件"""
    with open(local_path, "rb") as f:
        content = f.read()

    result = bucket.put_object(remote_path, content)
    if result.status == 200:
        print(f"  OK {remote_path}")
    else:
        print(f"  FAIL {remote_path} (status={result.status})")
    return result.status == 200


def main():
    print(f"Connecting OSS: {BUCKET_NAME} ({ENDPOINT})...")

    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)

    if not BUILD_DIR.exists():
        print(f"错误: build 目录不存在: {BUILD_DIR}")
        print("请先运行: cd src/studio && flutter build web --release")
        return

    print(f"Uploading from: {BUILD_DIR}")
    print("-" * 50)

    success = 0
    failed = 0

    for root, dirs, files in os.walk(BUILD_DIR):
        root_path = Path(root)

        for filename in files:
            local_path = root_path / filename
            relative = local_path.relative_to(BUILD_DIR)
            remote_path = str(relative).replace("\\", "/")

            if upload_file(bucket, local_path, remote_path):
                success += 1
            else:
                failed += 1

    print("-" * 50)
    print(f"完成: {success} 成功, {failed} 失败")
    print(f"访问: https://{BUCKET_NAME}.{ENDPOINT}")


if __name__ == "__main__":
    main()
