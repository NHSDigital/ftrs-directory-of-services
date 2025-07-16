# AWS WAF CloudWatch Log Group Resource Policy
resource "aws_cloudwatch_log_resource_policy" "waf_log_group_policy" {
  policy_document = data.aws_iam_policy_document.waf_log_group_policy_document.json
  policy_name     = "${local.resource_prefix}-${var.waf_log_group_policy_name}"
  provider        = aws.us-east-1
}

data "aws_iam_policy_document" "waf_log_group_policy_document" {
  version = "2012-10-17"
  statement {
    effect = "Allow"
    principals {
      identifiers = ["delivery.logs.amazonaws.com"]
      type        = "Service"
    }
    actions = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = [
      "arn:aws:logs:${var.aws_region_us_east_1}:${data.aws_caller_identity.current.account_id}:log-group:aws-waf-logs-ftrs-dos-${var.environment}*:log-stream:*"
    ]
    condition {
      test     = "ArnLike"
      values   = ["arn:aws:logs:${var.aws_region_us_east_1}:${data.aws_caller_identity.current.account_id}:*"]
      variable = "aws:SourceArn"
    }
    condition {
      test     = "StringEquals"
      values   = [tostring(data.aws_caller_identity.current.account_id)]
      variable = "aws:SourceAccount"
    }
  }
  provider = aws.us-east-1
}

# AWS OSIS & API Gateway CloudWatch Log Group Resource Policy
resource "aws_cloudwatch_log_resource_policy" "osis_apigw_log_group_policy" {
  policy_document = data.aws_iam_policy_document.osis_apigw_log_group_policy_document.json
  policy_name     = "${local.resource_prefix}-${var.osis_apigw_log_group_policy_name}"
}

data "aws_iam_policy_document" "osis_apigw_log_group_policy_document" {
  version = "2012-10-17"
  statement {
    effect = "Allow"
    principals {
      identifiers = ["delivery.logs.amazonaws.com"]
      type        = "Service"
    }
    actions = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = [
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/vendedlogs/OpenSearchIngestion/dynamodb-to-os-${var.environment}*:log-stream:*",
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/apigateway/ftrs-dos-${var.environment}*/default:log-stream:*"
    ]
    condition {
      test     = "ArnLike"
      values   = ["arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"]
      variable = "aws:SourceArn"
    }
    condition {
      test     = "StringEquals"
      values   = [tostring(data.aws_caller_identity.current.account_id)]
      variable = "aws:SourceAccount"
    }
  }
}
