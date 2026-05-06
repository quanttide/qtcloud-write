# 函数计算模块
variable "service_name" {
  type    = string
  default = "qtcloud-write"
}

variable "function_name" {
  type    = string
  default = "provider"
}

variable "region" {
  type = string
}

resource "alicloud_fc_service" "this" {
  service_name = var.service_name
}

resource "alicloud_fc_function" "this" {
  service_name  = alicloud_fc_service.this.service_name
  function_name = var.function_name
  runtime       = "custom-container"
  handler       = "main.handler"
  memory_size   = 512
  timeout       = 60

  container {
    image = "crpi-uorshhk4a32pmmio.cn-hangzhou.personal.cr.aliyuncs.com/quanttide/qtcloud-write-provider:latest"
  }
}

resource "alicloud_fc_trigger" "http_trigger" {
  service_name  = alicloud_fc_service.this.service_name
  function_name = alicloud_fc_function.this.function_name
  trigger_name   = "http-trigger"
  trigger_type   = "http"
  invocation_role = alicloud_ram_role.this.arn

  trigger_config = {
    authType = "anonymous"
    methods  = ["GET", "POST", "PUT", "DELETE"]
  }
}

resource "alicloud_ram_role" "this" {
  name = "${var.service_name}-fc-role"

  assume_role_policy = jsonencode({
    Version = "1"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["fc.aliyuncs.com"]
        }
      }
    ]
  })
}

resource "alicloud_ram_role_policy_attachment" "this" {
  role_name   = alicloud_ram_role.this.name
  policy_name  = "AliyunFCFullAccess"
  policy_type  = "System"
}

output "service_name" {
  value = alicloud_fc_service.this.service_name
}

output "function_name" {
  value = alicloud_fc_function.this.function_name
}

output "invoke_url" {
  value = "https://${alicloud_fc_service.this.service_name}.${var.region}.fc.aliyuncs.com/2016-08-15/proxy/${alicloud_fc_function.this.function_name}/"
}
