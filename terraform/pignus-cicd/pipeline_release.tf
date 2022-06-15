/*
  Pignus-CICD
  CodePipeline: Pignus-Release

*/

resource "aws_codepipeline" "pignus_release" {
  name     = "Pignus-Release"
  role_arn = data.aws_iam_role.catacomb_codepipeline.arn

  artifact_store {
    location = aws_s3_bucket.pignus_pipelines.bucket
    type     = "S3"

  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn    = var.codestar_arn
        FullRepositoryId = "PatchSimple/pignus"
        BranchName       = "main"
      }
    }
  }

  stage {
    name = "Test"

    action {
      name             = "Test"
      category         = "Test"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["unit_tests"]
      version          = "1"

      configuration = {
        ProjectName = "Pignus-CICD-Test-Unit"
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "Build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_docker"]
      version          = "1"

      configuration = {
        ProjectName = "Pignus-CICD-Build-Docker"
        EnvironmentVariables = jsonencode([
          {
            name  = "BUILD_TAG"
            value = "rc-latest"
          },
        ])
      }
    }
  }

  stage {
    name = "Deploy-Local"

    action {
      name             = "Deploy-Sentry"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["deploy_lambda_sentry"]
      version          = "1"

      configuration = {
        ProjectName = "Pignus-CICD-Deploy-Lambda"
        EnvironmentVariables = jsonencode([
          {
            name  = "FUNCTION_NAME"
            value = "Pignus-Sentry"
          },
          {
            name  = "IMAGE"
            value = "pignus/pignus"
          },
          {
            name  = "TAG"
            value = "rc-test-latest"
          }
        ])
      }
    }

    action {
      name             = "Deploy-Gateway"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["deploy_lambda_gateway"]
      version          = "1"

      configuration = {
        ProjectName = "Pignus-CICD-Deploy-Lambda"
        EnvironmentVariables = jsonencode([
          {
            name  = "FUNCTION_NAME"
            value = "Pignus-Gateway"
          },
          {
            name  = "IMAGE"
            value = "pignus/pignus"
          },
          {
            name  = "TAG"
            value = "rc-test-latest"
          }
        ])
      }
    }
  }

  stage {
    name = "Migrations"

    action {
      name             = "Migrate"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["migrations_out"]
      version          = "1"

      configuration = {
        ProjectName = "Pignus-CICD-Deploy-Migrations"
      }
    }
  }

  stage {
    name = "Regression"

    action {
      name             = "Regression-Api"
      category         = "Test"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["regression_test"]
      version          = "1"

      configuration = {
       ProjectName = "Pignus-CICD-Test-Regression-Api"
      }
    }

    action {
      name             = "Regression-Cli"
      category         = "Test"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["regression_out2"]
      version          = "1"

      configuration = {
        ProjectName = "Pignus-CICD-Test-Regression-Cli"
      }
    }

  }


  stage {
    name = "Deploy"

    action {
      name             = "Deploy-Public"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["deploy_public"]
      version          = "1"

      configuration = {
        ProjectName = "Pignus-CICD-Deploy-Public-ECR"
      }
    }
  }
}
