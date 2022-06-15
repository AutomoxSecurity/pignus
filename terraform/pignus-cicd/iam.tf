/*
  Pignus-CICD
  IAM
    Role: Pignus-CICD

*/

# CodeStar Connection
resource "aws_codestarconnections_connection" "catacomb_github" {
  name          = "Catacomb PatchSimple"
  provider_type = "GitHub"
}

resource "aws_iam_role" "pignus_cicd" {
  name = "Pignus-CICD"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "pignus_cicd" {
  role = aws_iam_role.pignus_cicd.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Condition = {
          "StringEqualsIfExists" : {
            "iam:PassedToService" : [
              "ec2.amazonaws.com"
            ]
          }
        },
        Resource : "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${var.aws_account}:log-group:/secops/pignus-cicd*"
      },
      {
        Effect   = "Allow"
        Action   = "codestar-connections:UseConnection"
        Resource = var.codestar_arn
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "autoscaling:*"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "lambda:UpdateFunctionCode"
        Resource = "arn:aws:lambda:${var.aws_region}:${var.aws_account}:function:Pignus-*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:GetBucketAcl",
          "s3:GetBucketLocation"
        ]
        Resource = "arn:aws:s3:::pignus-pipelines-${var.aws_account}*"
      },
      {
        Effect = "Allow",
        Action = [
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild",
          "codebuild:BatchGetBuildBatches",
          "codebuild:StartBuildBatch"
        ]
        Resource = "arn:aws:codebuild:${var.aws_region}:${var.aws_account}:project/*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:*",
          "ecr-public:*",
          "ecr:DescribeImages",
          "ecr:GetAuthorizationToken"
        ]
        Resource = [
          "arn:aws:ecr:${var.aws_region}:${var.aws_account}:repository/*",
          "*"
        ]
      },
      {
        Sid    = "GetAuthorizationToken"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr-public:GetAuthorizationToken",
          "sts:GetServiceBearerToken"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "codestar-connections:UseConnection"
        Resource = aws_codestarconnections_connection.catacomb_github.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:CreateGrant",
          "kms:GenerateDataKey",
          "kms:Decrypt"
        ]
        Resource = data.aws_kms_key.pignus.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:PutParameter",
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:${var.aws_account}:parameter/PIGNUS_*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:*",
        ]
        Resource = "arn:aws:lambda:${var.aws_region}:${var.aws_account}:function:Pignus-Sentry"
      }
    ]
  })
}


resource "aws_iam_role" "pignus_cicd_test_regression" {
  name = "Pignus-CICD-Test-Regression"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "pignus_cicd_test_regression" {
  role = aws_iam_role.pignus_cicd_test_regression.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Condition = {
          "StringEqualsIfExists" : {
            "iam:PassedToService" : [
              "ec2.amazonaws.com"
            ]
          }
        },
        Resource : "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${var.aws_account}:log-group:/secops/pignus-cicd*"
      },
      {
        Effect   = "Allow"
        Action   = "codestar-connections:UseConnection"
        Resource = var.codestar_arn
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "autoscaling:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:GetBucketAcl",
          "s3:GetBucketLocation"
        ]
        Resource = "arn:aws:s3:::pignus-pipelines-${var.aws_account}*"
      },
      {
        Effect = "Allow",
        Action = [
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild",
          "codebuild:BatchGetBuildBatches",
          "codebuild:StartBuildBatch"
        ]
        Resource = "arn:aws:codebuild:${var.aws_region}:${var.aws_account}:project/*"
      },
      {
        Effect   = "Allow"
        Action   = "codestar-connections:UseConnection"
        Resource = aws_codestarconnections_connection.catacomb_github.arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:CreateGrant",
          "kms:Decrypt"
        ]
        Resource = data.aws_kms_key.pignus.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${var.aws_account}:parameter/PIGNUS_*",
          "arn:aws:ssm:${var.aws_region}:${var.aws_account}:parameter/PIGNUS_API_KEY_CLUSTER"
          ]
      }
    ]
  })
}
