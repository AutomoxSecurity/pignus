/*
  Pignus-Api
  IAM
    Roles
      Pignus-CodeBuild
      Pignus-Lambda
      Pignus-ApiGateway

*/

# Pignus CodeBuild
# Role for all Sync and Scan jobs
resource "aws_iam_role" "pignus_codebuild" {
  name = "Pignus-CodeBuild"

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

resource "aws_iam_role_policy" "pignus_codebuild" {
  role = aws_iam_role.pignus_codebuild.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:GetLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${var.aws_account}:log-group:/aws/lambda/*",
          "arn:aws:logs:${var.aws_region}:${var.aws_account}:log-group:/secops/codebuild/*",
          "arn:aws:logs:${var.aws_region}:${var.aws_account}:log-group:/pignus/*",
          "*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:GetLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${var.aws_account}:log-group:/pignus/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:DescribeKey",
          "kms:CreateGrant",
          "kms:Decrypt",
          "kms:RetireGrant"
        ]
        Resource = [
          data.aws_kms_key.pignus.arn,
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "codebuild:*",
        ]
        Resource = [
          "arn:aws:codebuild:${var.aws_region}:${var.aws_account}:project/Pignus-Sync-Container",
          "arn:aws:codebuild:${var.aws_region}:${var.aws_account}:project/Pignus-Scan-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSubnets",
          "ec2:CreateNetworkInterfacePermission",
          "ec2:*"
        ]
        Resource = [
          "*",
          "arn:aws:ec2:${var.aws_region}:${var.aws_account}:network-interface/*",
        ]
      },
      {
        Effect   = "Allow"
        Action   = "ssm:GetParameters"
        Resource = "arn:aws:ssm:${var.aws_region}:${var.aws_account}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "inspector2:ListFindings",
          "inspector2:ListCoverage",
        ]
        Resource = [
          "arn:aws:inspector2:${var.aws_region}:${var.aws_account}:/findings/list",
          "arn:aws:inspector2:${var.aws_region}:${var.aws_account}:/coverage/list"
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
        Effect = "Allow"
        Action = [
          "ecr:*",
          "ecr:DescribeImages",
          "ecr:GetAuthorizationToken"
        ]
        Resource = [
          "*",
          "arn:aws:ecr:${var.aws_region}:${var.aws_account}:repository/*"
        ]
      }
    ]
  })
}
