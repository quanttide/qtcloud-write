# OSS 模块 - 存储 Flutter Web 构建产物
variable "bucket_name" {
  type    = string
  default = "qtcloud-write-studio"
}

variable "region" {
  type = string
}

resource "alicloud_oss_bucket" "this" {
  bucket = var.bucket_name
  acl    = "public-read"

  lifecycle_rule {
    name      = "default"
    enabled   = "true"
    precedence = 0
  }
}

resource "alicloud_oss_bucket_cors" "this" {
  bucket = alicloud_oss_bucket.this.id

  rule {
    allowed_origins = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_headers = ["*"]
    max_age_seconds = 3600
  }
}

output "bucket_name" {
  value = alicloud_oss_bucket.this.bucket
}

output "endpoint" {
  value = "https://${alicloud_oss_bucket.this.bucket}.oss-${var.region}.aliyuncs.com"
}
