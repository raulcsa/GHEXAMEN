# Terraform configuration file for infrastructure (Mock)
terraform {
  required_version = ">= 1.0"
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

resource "null_resource" "monorepo_env" {
  provisioner "local-exec" {
    command = "echo 'Deploying monorepo infrastructure v2...'"
  }
}
