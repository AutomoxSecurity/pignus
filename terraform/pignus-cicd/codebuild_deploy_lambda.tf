/*
  Pignus-CICD
  CodeBuild: Deploy-Lambda
  Deploys a Docker Image to a Lambda.

*/

resource "aws_codebuild_project" "deploy_lambda" {
  name          = "Pignus-CICD-Deploy-Lambda"
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
      value = "pignus/pignus"
    }
    environment_variable {
      name  = "FUNCTION_NAME"
      value = ""
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.pignus_cicd.name
      stream_name = "Deploy-Lambda"
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = file("${path.module}/buildspecs/deploy_lambda.yaml")
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
