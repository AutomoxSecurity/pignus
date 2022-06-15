/*
  Pignus-Api
  CodeBuild: Pignus-Sync-Image
  Job to download a given docker url  into the local AWS account ECR.

*/

resource "aws_cloudwatch_log_group" "sync_image" {
  name = "/pignus/sync-image"
  retention_in_days = 365

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

resource "aws_codebuild_project" "pignus_sync" {
  name          = "Pignus-Sync-Image"
  description   = "Import a given Docker Image into the local ECR repository for Pignus"
  build_timeout = "20"
  service_role  = aws_iam_role.pignus_codebuild.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "AWS_ACCOUNT"
      value = var.aws_account
    }
    environment_variable {
      name  = "AWS_REGION"
      value = var.aws_region
    }
    environment_variable {
      name  = "REPOSITORY"
      value = "docker.io"
    }
    environment_variable {
      name  = "IMAGE"
      value = "alpine"
    }
    environment_variable {
      name  = "TAG"
      value = ""
    }
    environment_variable {
      name  = "DIGEST"
      value = ""
    }
    environment_variable {
      name  = "FROM_AWS_ACCOUNT"
      value = ""
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.sync_image.name
      stream_name = "Pignus-Sync-Image"
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = file("${path.module}/buildspecs/sync-image.yaml")
  }

  source_version = "master"

  vpc_config {
    vpc_id             = aws_vpc.pignus.id
    subnets            = [aws_subnet.pignus_private_b.id]
    security_group_ids = [aws_security_group.pignus_egress_all.id]
  }

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

# End File: automox/pignus/terraform/pignus-api/codebuild_sync_image.tf
