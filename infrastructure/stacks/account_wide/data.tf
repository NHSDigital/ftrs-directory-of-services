data "aws_acm_certificate" "vpn_cert" {
  count = var.environment == "dev" ? 1 : 0

  domain      = "${local.account_prefix}-vpn"
  types       = ["IMPORTED"]
  statuses    = ["ISSUED"]
  most_recent = true
}

data "aws_availability_zones" "available_azs" {
  state = "available"
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = var.performance_ami_name_pattern
  }
  filter {
    name   = "architecture"
    values = var.performance_ami_architectures
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

data "aws_subnet" "vpc_private_subnets_by_count" {
  count = length(module.vpc.private_subnets)
  id    = module.vpc.private_subnets[count.index]
}

data "aws_iam_policy_document" "regional_waf_log_group_policy_document" {
  version = "2012-10-17"
  statement {
    effect = "Allow"
    principals {
      identifiers = ["delivery.logs.amazonaws.com"]
      type        = "Service"
    }
    actions = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = [
      "arn:aws:logs:${var.aws_region}:${local.account_id}:log-group:aws-waf-logs-ftrs-dos-${var.environment}-${var.regional_waf_log_group}:log-stream:*"
    ]
    condition {
      test     = "ArnLike"
      values   = ["arn:aws:logs:${var.aws_region}:${local.account_id}:*"]
      variable = "aws:SourceArn"
    }
    condition {
      test     = "StringEquals"
      values   = [tostring(local.account_id)]
      variable = "aws:SourceAccount"
    }
  }
}
