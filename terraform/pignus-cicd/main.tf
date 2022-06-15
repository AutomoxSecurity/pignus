/*
  Pignus-CICD
  This project controls the CICD of Pignus.

  CodePipelines
    Pignus-Develop
    Pignus-Release
    
  CodeBuilds
    Pignus-CICD-Test-Unit
    Pignus-CICD-Build-Docker
    Pignus-CICD-Deploy-Lambda
    Pignus-CICD-Deploy-Lambda-Automox

  IAM
    Role Pignus-CICD

*/

variable "aws_account" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "pignus_version" {
  type    = string
  default = "0.6.3"
}

variable "pignus_branch" {
  type = string
}

variable "pignus_public_ecr" {

  type = string
}

variable "pignus_api_url" {
  type = string
}

variable "codestar_arn" {
  type = string
}

resource "aws_s3_bucket" "pignus_pipelines" {
  bucket = "pignus-pipelines-${var.aws_account}"
  acl    = "private"

  tags = {
    Name      = "pignus-pipelines"
    team      = "secops"
    terraform = "true"
    app       = "pignus-cicd"
  }
}

resource "aws_cloudwatch_log_group" "pignus_cicd" {
  name = "/secops/pignus-cicd"

  retention_in_days = 365
  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus-cicd"
  }
}

# Create the private Pignus Ecr repository
resource "aws_ecr_repository" "pignus_pignus" {
  name                 = "pignus/pignus"
  image_tag_mutability = "MUTABLE"

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = data.aws_kms_key.pignus.arn
  }

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Create the public ECR repository
resource "aws_ecrpublic_repository" "pignus" {
  provider = aws.east

  repository_name = "pignus/pignus"

  catalog_data {
    about_text = "About Text"
    # architectures     = ["ARM"]
    description = ""
    # logo_image_blob   = filebase64(image.png)
    operating_systems = ["Linux"]
    usage_text        = "Usage Text"
  }
}
