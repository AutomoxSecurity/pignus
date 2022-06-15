/*
  Pignus-Api
  Lambda: Pignus-Gateway
  Lambda to serve requests stemming from the Pignus Api Gateway.

*/
# Pignus Lambda Role
# Role for Lambda Functions to run under
resource "aws_iam_role" "pignus_lambda_gateway" {
  name = "Pignus-Lambda-Gateway"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      }
    },
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      }
    },
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      }
    },
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "config.amazonaws.com"
      }
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "pignus_lambda_gateway" {
  role = aws_iam_role.pignus_lambda_gateway.name

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
          "ecr:*",
        ]
        Resource = [
          "arn:aws:ecr:${var.aws_region}:${var.aws_account}:repository/*"
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
        Action = [
          "codebuild:*",
        ]
        Resource = "arn:aws:codebuild:${var.aws_region}:${var.aws_account}:project/Pignus-*"
        Effect   = "Allow"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSubnets"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "inspector2:ListFindings"
        Resource = "arn:aws:inspector2:${var.aws_region}:${var.aws_account}:/findings/list"
      },
      {
        Effect = "Allow"
        Action = [
          "lamdba:*"
        ]
        Resource = [
          "*",
          "arn:aws:lambda:${var.aws_region}:${var.aws_account}:function:Pignus-Gateway*",
          "arn:aws:lambda:${var.aws_region}:${var.aws_account}:function:Pignus-Sentry*",

        ]
      },
    ]
  })
}


resource "aws_lambda_function" "pignus_gateway" {
  function_name = "Pignus-Gateway"
  role          = aws_iam_role.pignus_lambda_gateway.arn
  kms_key_arn   = data.aws_kms_key.pignus.arn
  package_type  = "Image"
  image_uri     = var.pignus_image
  timeout       = 900

  environment {
    variables = {
      PIGNUS_AWS_ACCOUNT  = var.aws_account
      PIGNUS_AWS_REGION   = var.aws_region
      PIGNUS_AWS_KMS      = data.aws_kms_key.pignus.arn
      PIGNUS_RELEASE_ENV  = "TEST"
      PIGNUS_DB_HOST      = aws_db_instance.pignus_db.address
      PIGNUS_DB_NAME      = var.pignus_database_name
      PIGNUS_DB_USER      = data.aws_ssm_parameter.pignus_rds_admin_user.value
      PIGNUS_DB_PASS      = data.aws_ssm_parameter.pignus_rds_admin_pass.value
      PIGNUS_KEY_PATH     = "/mnt/keys"
      PIGNUS_DEBUG        = var.pignus_debug

    }
  }
  tracing_config {
    mode = "Active"
  }

  file_system_config {
    arn              = aws_efs_access_point.pignus_keys.arn
    local_mount_path = "/mnt/keys"
  }

  vpc_config {
    subnet_ids = [
      aws_subnet.pignus_public_a.id,
      aws_subnet.pignus_public_b.id,
      aws_subnet.pignus_private_b.id
    ]
    security_group_ids = [
      aws_security_group.pignus_lambda_rds.id,
      aws_security_group.pignus_egress_all.id,
      aws_security_group.pignus_efs.id
    ]
  }

  depends_on = [aws_db_instance.pignus_db, aws_efs_access_point.pignus_keys]

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}
