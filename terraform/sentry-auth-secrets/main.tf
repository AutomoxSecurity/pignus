# Pignus Sentry Auth Secrets
# This project manages:
#   - KMS key for Pignus to utilize
#   - SSM parameter for the Pignus Api key

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.39.0"
    }
  }

  backend "s3" {
    key    = "terraform/pignus-secrets.tfstate"
    region = "us-west-2"
  }
}

variable "pignus_api_key" {
  type = string
}

# Create KMS Key for Pignus
resource "aws_kms_key" "pignus" {
  description = "Key for encrypting pignus resources"
  tags = {
    team      = "secops"
    terraform = "true"
  }
}
resource "aws_kms_alias" "pignus" {
  name          = "alias/pignus"
  target_key_id = aws_kms_key.pignus.key_id
}

# Secret Manager Parameters
resource "aws_ssm_parameter" "pignus_api_key" {
  name        = "pignus_api_key"
  description = "Api key for the Pignus Api"
  type        = "SecureString"
  value       = var.pignus_api_key
  key_id      = aws_kms_alias.pignus.id

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

