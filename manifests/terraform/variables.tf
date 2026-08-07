variable "region" {
  description = "Alibaba Cloud region."
  type        = string
  default     = "cn-hangzhou"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "prod"
}

variable "llm_api_key" {
  description = "DeepSeek API key for the provider function. Set with TF_VAR_llm_api_key."
  type        = string
  sensitive   = true
  default     = ""
}

variable "container_image" {
  description = "Full ACR image URL for the provider function container."
  type        = string
}

variable "llm_base_url" {
  description = "OpenAI-compatible LLM base URL."
  type        = string
  default     = "https://api.deepseek.com"
}
