# Pignus Sentry Auth Ecr Auth Lambda

resource "aws_lambda_function" "pignus_sentry_ecr_auth" {
  function_name = "Pignus-Sentry-Ecr-Auth"
  role          = data.aws_iam_role.pignus.arn
  kms_key_arn   = data.aws_kms_key.pignus.arn
  package_type  = "Image"
  image_uri     = "${var.aws_account}.dkr.ecr.${var.aws_region}.amazonaws.com/changeme/pignus:${var.pignus_tag}"
  timeout       = 900

  environment {
    variables = {
      PIGNUS_AWS_ACCOUNT = var.aws_account
      PIGNUS_AWS_REGION  = var.aws_region
      PIGNUS_AWS_KMS     = data.aws_kms_key.pignus.arn
      PIGNUS_API_UA      = "sentry-auth-${var.aws_account}"
      PIGNUS_API_URL     = var.pignus_api_url
      PIGNUS_API_KEY     = "${data.aws_ssm_parameter.pignus_api_key.value}"
    }
  }

  tracing_config {
    mode = "Active"
  }

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}


resource "aws_cloudwatch_event_rule" "pignus_cron" {
  name                = "Pignus-ECR-Auth-Cron"
  description         = "Run Pignus ECR Auth Lambda on a cron schedule."
  schedule_expression = "rate(60 minutes)"
}


resource "aws_cloudwatch_event_target" "pignus_cron_target" {
  arn   = aws_lambda_function.pignus_sentry_ecr_auth.arn
  rule  = aws_cloudwatch_event_rule.pignus_cron.id
  input = <<JSON
{
  "action": "image-auth"
}
JSON
}
