/*
  Pignus-CICD
  CodePipeline: Pignus-Develop

*/

resource "aws_codepipeline" "pignus_develop" {
  name = "Pignus-Develop"
  # role_arn = aws_iam_role.pignus_cicd.arn
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
        ConnectionArn        = var.codestar_arn
        FullRepositoryId     = "PatchSimple/pignus"
        BranchName           = var.pignus_branch
        OutputArtifactFormat = "CODEBUILD_CLONE_REF"
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
      output_artifacts = ["unit_test_out"]
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
      output_artifacts = ["build_out"]
      version          = "1"

      configuration = {
        ProjectName = "Pignus-CICD-Build-Docker"
      }
    }
  }

  stage {
    name = "Deploy-to-Lambda"

    action {
      name             = "Deploy-Sentry"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["deploy_sentry_out"]
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
            value = "${var.pignus_branch}-latest"
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
      output_artifacts = ["deploy_gateway_out"]
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
            value = "${var.pignus_branch}-latest"
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
      output_artifacts = ["regression_out"]
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

}
