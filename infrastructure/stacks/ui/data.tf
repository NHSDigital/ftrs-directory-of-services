data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }

  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc-private-*"]
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}

data "aws_iam_role" "app_github_runner_iam_role" {
  name = "${var.repo_name}-${var.app_github_runner_role_name}"
}

data "aws_ssm_parameter" "dos_aws_account_id_mgmt" {
  name = "/dos/${var.environment}/aws_account_id_mgmt"
}

data "aws_iam_policy_document" "secrets_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:/${var.project}/${var.environment}/cis2-private-key*",
      "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:/${var.project}/${var.environment}/cis2-public-key*",
      aws_secretsmanager_secret.session_secret.arn,
    ]
  }
}

data "aws_iam_policy_document" "ssm_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/${var.project}-${var.environment}-crud-apis${local.workspace_suffix}/endpoint",
      "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/${var.project}/${var.environment}/cis2-client-config"
    ]
  }
}

data "aws_iam_policy_document" "secrets_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${var.project}/${var.environment}${var.workspace_suffix}/",
      "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${var.project}/${var.environment}/cis2-*"
    ]
  }
}

# TODO: FDOS-378 - This is overly permissive and should be resolved when we have control over stack deployment order.
data "aws_iam_policy_document" "execute_api_policy" {
  statement {
    effect = "Allow"
    actions = [
      "execute-api:Invoke"
    ]
    resources = [
      "arn:aws:execute-api:*:*:*/*/*/*/*"
    ]
  }
}

data "aws_wafv2_web_acl" "waf_web_acl" {
  name     = "${var.project}-${var.environment}-account-wide-${var.waf_name}"
  scope    = var.waf_scope
  provider = aws.us-east-1
}

data "aws_route53_zone" "main" {
  name = local.env_domain_name
}

data "aws_acm_certificate" "domain_cert" {
  provider    = aws.us-east-1
  domain      = "*.${local.env_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}

data "aws_iam_policy_document" "dynamodb_session_store_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query"
    ]
    resources = [
      module.ui_session_store.dynamodb_table_arn,
      "${module.ui_session_store.dynamodb_table_arn}/index/*"
    ]
  }
}

data "aws_cloudfront_cache_policy" "caching_disabled" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_origin_request_policy" "all_viewer_headers" {
  name = "Managed-AllViewerExceptHostHeader"
}
