/*
  Pignus-CICD
  CodeBuild: Deploy-Migrations
  Deploys a Docker Image to a Lambda.

*/

resource "aws_codebuild_project" "deploy_migrations" {
  name          = "Pignus-CICD-Deploy-Migrations"
  description   = ""
  build_timeout = "20"
  service_role  = aws_iam_role.pignus_cicd.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "FUCNTION_NAME"
      value = "Pignus-Sentry"
    }
    environment_variable {
      name  = "FUCNTION_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "PAYLOAD_ACTION"
      value = "migrations"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.pignus_cicd.name
      stream_name = "Deploy-Migrations"
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = file("${path.module}/buildspecs/execute_lambda.yaml")
  }

  source_version = "main"

  vpc_config {
    vpc_id             = data.aws_vpc.pignus.id
    subnets            = [data.aws_subnet.pignus_cicd_subnet_b_id.id]
    security_group_ids = [data.aws_security_group.pignus_cicd.id]
  }

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus-cicd"
  }
}
