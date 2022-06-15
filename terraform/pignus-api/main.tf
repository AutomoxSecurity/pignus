/*
  Pignus-Api
  Creates Resources:
    ApiGateway
      Pignus
    CodeBuild
      Pignus-Image-Sync
      Pignus-Scan-Aws
      Pignus-Scan-Crowdstrike
    Cloudwatch Log group
      /pignus

*/


# Create the FileSystem for Pignus RSA keys
resource "aws_efs_file_system" "pignus_keys" {
  encrypted = true
  kms_key_id = data.aws_kms_key.pignus.arn
  # availability_zone_name = "${var.aws_region}b"
  tags = {
    Name = "Pignus Keys"
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

resource "aws_efs_access_point" "pignus_keys" {
  depends_on     = [aws_efs_file_system.pignus_keys]
  file_system_id = aws_efs_file_system.pignus_keys.id
  posix_user {
    uid = 1000
    gid = 1000
  }
  root_directory {
    creation_info {
      owner_gid = 1000
      owner_uid = 1000
      permissions = 777
    }
    path = "/mnt/keys"
  }

}


resource "aws_efs_mount_target" "pignus_keys_a" {
  file_system_id = aws_efs_file_system.pignus_keys.id
  subnet_id      = aws_subnet.pignus_public_a.id
  security_groups = [aws_security_group.pignus_efs.id]
}


resource "aws_efs_mount_target" "pignus_keys_b" {
  file_system_id = aws_efs_file_system.pignus_keys.id
  subnet_id      = aws_subnet.pignus_private_b.id
  security_groups = [aws_security_group.pignus_efs.id]
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
