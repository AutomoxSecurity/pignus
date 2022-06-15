resource "aws_iam_role" "pignus" {
  name = "Pignus"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "pignus" {
  role = aws_iam_role.pignus.name

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
          "ecr:*",
        ]
        Resource = "arn:aws:ecr:${var.aws_region}:${var.aws_account}:repository/*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:DescribeKey",
          "kms:CreateGrant",
          "kms:Decrypt"
        ]
        Resource = data.aws_kms_key.pignus.arn
      },
    ]
  })
}

data "aws_iam_role" "pignus" {
  name = aws_iam_role.pignus.name
}
