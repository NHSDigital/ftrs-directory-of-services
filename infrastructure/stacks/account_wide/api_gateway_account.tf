resource "aws_api_gateway_account" "api_gateway_account" {
  cloudwatch_role_arn = aws_iam_role.cloudwatch_api_gateway_role.arn
}

resource "aws_iam_role" "cloudwatch_api_gateway_role" {
  name               = "${var.project}_api_gateway_cloudwatch_global"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role_policy" "api_gateway_cloudwatch_policy" {
  name = "${var.project}-api-gateway-cloudwatch"
  role = aws_iam_role.cloudwatch_api_gateway_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${local.account_id}:log-group:/aws/api-gateway/*"
        ]
      }
    ]
  })
}
