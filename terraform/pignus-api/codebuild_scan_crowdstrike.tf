/*
  Pignus-Api
  CodeBuild: Pignus-Scan-CrowdStrike
  Container scanning via CrowdStrike's container scanning tool.

*/

resource "aws_cloudwatch_log_group" "scan_crowdstrike" {
  name = "/pignus/scan-crowdstrike"
  retention_in_days = 365

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

resource "aws_codebuild_project" "scan_crowdstrike" {
  name          = "Pignus-Scan-Crowdstrike"
  description   = ""
  build_timeout = "5"
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
      name  = "IMAGE"
      value = ""
    }
    environment_variable {
      name  = "TAG"
      value = "latest"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.scan_crowdstrike.name
      stream_name = "Pignus-Scan-Crowdstrike"
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = file("${path.module}/buildspecs/scan-crowdstrike.yaml")
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

# End File: automox/pignus/terraform/pignus-api/codebuild_scan_crowdstrike.tf
