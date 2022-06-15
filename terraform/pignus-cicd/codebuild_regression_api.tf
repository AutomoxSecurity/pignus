/*
  Pignus-CICD
  CodeBuild: Test-Regression
  Unit test the Pignus python application.

*/

resource "aws_codebuild_project" "build_test_regression_api" {
  name          = "Pignus-CICD-Test-Regression-Api"
  description   = ""
  build_timeout = "20"
  service_role  = aws_iam_role.pignus_cicd_test_regression.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "PIGNUS_API_URL"
      value = var.pignus_api_url
    }
    environment_variable {
      name  = "PIGNUS_RELEASE_ENV"
      value = "TEST"
    }

    environment_variable {
      name  = "PIGNUS_API_UA"
      value = "CODEBUILD-REGRESSION"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = aws_cloudwatch_log_group.pignus_cicd.name
      stream_name = "Test-Regression-Api"
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = file("${path.module}/buildspecs/test_regression_api.yaml")
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
