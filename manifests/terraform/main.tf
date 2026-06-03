terraform {
  required_version = ">= 1.6.0"

  required_providers {
    alicloud = {
      source  = "hashicorp/alicloud"
      version = "~> 1.230.0"
    }
  }

  backend "oss" {
    bucket  = "qtcloud-write-terraform-state"
    prefix  = "state"
    region  = "cn-hangzhou"
    encrypt = true
  }
}

provider "alicloud" {
  region = var.region
}

module "oss" {
  source = "./modules/oss"

  bucket_name = "qtcloud-write-studio"
  region      = var.region
}

module "fc" {
  source = "./modules/fc"

  service_name  = "qtcloud-write"
  function_name = "provider"
  region        = var.region
  llm_api_key   = var.llm_api_key
  llm_base_url  = var.llm_base_url
}
