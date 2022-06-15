/*
  Pignus-CICD
  External
  Pulls in IAC units used by Pignus CICD but are not directly built or controlled by Pignus CICD.

*/

# Catacomb Inheritance
# Pignus CICD VPC
variable "pignus_cicd_vpc_id" {
  type = string
}
data "aws_vpc" "pignus" {
  id = var.pignus_cicd_vpc_id
}

# Pignus CICD subnet
variable "pignus_cicd_subnet_b_id" {
  type = string
}
data "aws_subnet" "pignus_cicd_subnet_b_id" {
  id = var.pignus_cicd_subnet_b_id
}
# Pignus CICD security group
variable "pignus_cicd_security_group_id" {
  type = string
}
data "aws_security_group" "pignus_cicd" {
  id = var.pignus_cicd_security_group_id
}
# Pignus CICD log group
data "aws_cloudwatch_log_group" "pignus" {
  name = "/secops/codebuild/catacomb"
}
data "aws_iam_role" "catacomb_codebuild" {
  name = "catacomb-codebuild"
}
data "aws_iam_role" "catacomb_codepipeline" {
  name = "catacomb-codebuild-pipeline"
}

# Pignus-Api-Secrets Inheritance
data "aws_kms_key" "pignus" {
  key_id = "alias/pignus"
}

data "aws_ssm_parameter" "pignus_api_key" {
  name = "PIGNUS_API_KEY_DEV_ROLE_ADMIN"
}