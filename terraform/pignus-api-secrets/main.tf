# Pignus Api Secrets
# This project manages:
#   - KMS key for Pignus to utilize
#   - SSM parameters for RDS
#      - PIGNUS_RDS_ADMIN_USER
#      - PIGNUS_RDS_ADMIN_PASS
#      - PIGNUS_RDS_APP_USER
#      - PIGNUS_RDS_APP_PASS
#

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.39.0"
    }
  }

  backend "s3" {
    key    = "terraform/pignus-api-secrets.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = "us-west-2"
}

provider "aws" {
  alias  = "east"
  region = "us-east-1"
}


# Create KMS Key for Pignus
resource "aws_kms_key" "pignus" {
  description         = "Key for encrypting Pignus resources"
  enable_key_rotation = true
  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}
resource "aws_kms_alias" "pignus" {
  name          = "alias/pignus"
  target_key_id = aws_kms_key.pignus.key_id
}


# Create the Pignus RDS admin user and password
variable "pignus_rds_admin_user" {
  type = string
}
resource "aws_ssm_parameter" "pignus_rds_admin_user" {
  name        = "PIGNUS_RDS_ADMIN_USER"
  description = "Admin user for Pignus RDS"
  type        = "SecureString"
  value       = var.pignus_rds_admin_user
  key_id      = aws_kms_alias.pignus.id

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

variable "pignus_rds_admin_pass" {
  type = string
}
resource "aws_ssm_parameter" "pignus_rds_admin_pass" {
  name        = "PIGNUS_RDS_ADMIN_PASS"
  description = "Admin password for Pignus RDS"
  type        = "SecureString"
  value       = var.pignus_rds_admin_pass
  key_id      = aws_kms_alias.pignus.id

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}


# Create the Pignus RDS application user
variable "pignus_rds_app_user" {
  type = string
}
resource "aws_ssm_parameter" "pignus_rds_app_user" {
  name        = "PIGNUS_RDS_APP_USER"
  description = "App user for Pignus RDS"
  type        = "SecureString"
  value       = var.pignus_rds_app_user
  key_id      = aws_kms_alias.pignus.id

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}


variable "pignus_rds_app_pass" {
  type = string
}
resource "aws_ssm_parameter" "pignus_rds_app_pass" {
  name        = "PIGNUS_RDS_APP_PASS"
  description = "App password for Pignus RDS"
  type        = "SecureString"
  value       = var.pignus_rds_app_pass
  key_id      = aws_kms_alias.pignus.id

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}
