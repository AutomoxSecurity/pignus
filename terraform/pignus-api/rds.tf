/*
  Pignus-Api
  RDS
  Creates the RDS MySQL database for Pignus

*/

resource "aws_db_instance" "pignus_db" {
  name                                = "pignus"
  identifier                          = "pignus"
  allocated_storage                   = 20
  engine                              = "mysql"
  engine_version                      = "8.0.26"
  instance_class                      = "db.t2.small"
  auto_minor_version_upgrade          = true
  backup_retention_period             = 31
  delete_automated_backups            = false
  deletion_protection                 = true
  iam_database_authentication_enabled = true
  storage_encrypted                   = true
  kms_key_id                          = data.aws_kms_key.pignus.arn
  username                            = data.aws_ssm_parameter.pignus_rds_admin_user.value
  password                            = data.aws_ssm_parameter.pignus_rds_admin_pass.value
  db_subnet_group_name                = "pignus"
  vpc_security_group_ids = [
    aws_security_group.pignus_rds_ingress.id,
    # aws_security_group.pignus_netskope.id
  ]

  depends_on = [aws_db_subnet_group.pignus]
  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

# End File: automox/pignus/terraform/pignus-api/rds.tf
