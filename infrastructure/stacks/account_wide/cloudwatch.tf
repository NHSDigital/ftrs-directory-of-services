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

resource "aws_cloudwatch_log_group" "waf_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  name              = "${var.waf_log_group_name_prefix}${local.resource_prefix}-${var.waf_log_group}"
  retention_in_days = var.waf_log_group_retention_days
  log_group_class   = var.waf_log_group_class
  provider          = aws.us-east-1
}

resource "aws_cloudwatch_log_group" "regional_waf_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  name              = "${var.waf_log_group_name_prefix}${local.account_prefix}-${var.regional_waf_log_group}"
  retention_in_days = var.regional_waf_log_group_retention_days
  log_group_class   = var.regional_waf_log_group_class
}

resource "aws_cloudwatch_log_resource_policy" "regional_waf_log_group_policy" {
  policy_document = data.aws_iam_policy_document.regional_waf_log_group_policy_document.json
  policy_name     = "${local.resource_prefix}-${var.regional_waf_log_group_policy_name}"
}

resource "aws_wafv2_web_acl_logging_configuration" "regional_waf_logging_configuration" {
  log_destination_configs = [aws_cloudwatch_log_group.regional_waf_log_group.arn]
  resource_arn            = aws_wafv2_web_acl.regional_waf_web_acl.arn

  depends_on = [aws_cloudwatch_log_resource_policy.regional_waf_log_group_policy]
}

resource "aws_cloudwatch_log_group" "firehose_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  name              = "${local.resource_prefix}-${var.firehose_log_group_name}"
  retention_in_days = var.firehose_logs_retention_in_days
}

resource "aws_cloudwatch_log_group" "performance_ec2_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  # checkov:skip=CKV_AWS_338: Justification: These are internal logs for the running of performance tests. They do
  #                                          not need to be kept for at least one year.
  name              = "${var.performance_ec2_log_group_name_prefix}${local.resource_prefix}-${var.performance_ec2_log_group}"
  retention_in_days = var.performance_ec2_log_group_retention_days
  log_group_class   = var.performance_ec2_log_group_class
}
