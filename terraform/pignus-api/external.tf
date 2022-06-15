/*
  Pignus-Api
  External
    KMS
    SSM

*/

# KMS Key: Pignus
# This key is created by Pignus-Api-Secrets.
# It used used to encrypt:
#   RDS Pignus
#   ECR Repositories
data "aws_kms_key" "pignus" {
  key_id = "alias/pignus"
}

# SSM Parameter: PIGNUS_RDS_APP_USER
data "aws_ssm_parameter" "pignus_db_user" {
  name = "PIGNUS_RDS_APP_USER"
}

# SSM Parameter: PIGNUS_RDS_APP_PASS
data "aws_ssm_parameter" "pignus_db_pass" {
  name = "PIGNUS_RDS_APP_PASS"
}

# SSM Parameter: PIGNUS_RDS_ADMIN_USER
data "aws_ssm_parameter" "pignus_rds_admin_user" {
  name = "PIGNUS_RDS_ADMIN_USER"
}

# SSM Parameter: PIGNUS_RDS_ADMIN_PASS
data "aws_ssm_parameter" "pignus_rds_admin_pass" {
  name = "PIGNUS_RDS_ADMIN_PASS"
}


# End File: automox/pignus/terraform/pignus-api/external.tf
