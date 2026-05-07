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

variable "llm_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "llm_base_url" {
  type    = string
  default = "https://api.deepseek.com"
}

resource "alicloud_fc_service" "this" {
  name = var.service_name
  role = alicloud_ram_role.this.arn
}

resource "alicloud_fc_function" "this" {
  service     = alicloud_fc_service.this.name
  name        = var.function_name
  runtime     = "custom-container"
  handler     = "main.handler"
  memory_size = 512
  timeout     = 60
  ca_port     = 9000

  custom_container_config {
    image   = "${{ vars.ACR_REGISTRY }}/quanttide/qtcloud-write-provider:latest"
    command = "uv"
    args    = "run uvicorn app.main:app --host 0.0.0.0 --port 9000"
  }

  environment_variables = {
    llm_api_key  = var.llm_api_key
    llm_base_url = var.llm_base_url
  }
}

resource "alicloud_fc_trigger" "http_trigger" {
  service  = alicloud_fc_service.this.name
  function = alicloud_fc_function.this.name
  name     = "http-trigger"
  type     = "http"

  config = jsonencode({
    authType = "anonymous"
    methods  = ["GET", "POST", "PUT", "DELETE"]
  })
}

resource "alicloud_ram_role" "this" {
  name = "${var.service_name}-fc-role"

  document = jsonencode({
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
  policy_name = "AliyunFCFullAccess"
  policy_type = "System"
}

output "service_name" {
  value = alicloud_fc_service.this.name
}

output "function_name" {
  value = alicloud_fc_function.this.name
}

output "invoke_url" {
  value = "https://${alicloud_fc_service.this.name}.${var.region}.fc.aliyuncs.com/2016-08-15/proxy/${alicloud_fc_function.this.name}/"
}
