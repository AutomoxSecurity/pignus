/*
  Pignus-CICD
  CodePipeline: Pignus-Feature-Alix

*/

resource "aws_codepipeline" "pignus_feature_alix" {
  name     = "Pignus-Feature-Alix"
  role_arn = aws_iam_role.pignus_cicd.arn

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
        BranchName           = "feature/alix"
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
        EnvironmentVariables = jsonencode([
          {
            name  = "BUILD_TAG"
            value = "${var.pignus_branch}-latest"
          },
          {
            name  = "PIGNUS_AWS_ACCOUNT"
            value = var.aws_account
          },
          {
            name  = "PIGNUS_AWS_REGION"
            value = var.aws_region
          }
        ])
      }
    }
  }

}
