# Pignus Sentry Auth
variable "aws_account" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "pignus_api_url" {
  type = string
}

variable "pignus_tag" {
  type = string
}

data "aws_kms_key" "pignus" {
  key_id = "alias/pignus"
}

data "aws_ssm_parameter" "pignus_api_key" {
  name = "pignus_api_key"
}

resource "aws_ecr_repository" "pignus_pignus" {
  name                 = "pignus/pignus"
  image_tag_mutability = "MUTABLE"
  tags = {
    team      = "secops"
    terraform = "true"
  }

  image_scanning_configuration {
    scan_on_push = true
  }

}
