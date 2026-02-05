data "aws_vpc" "vpc" {
  count = local.stack_enabled
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  count = local.stack_enabled
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc[0].id]
  }

  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc-private-*"]
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = local.stack_enabled == 1 ? toset(data.aws_subnets.private_subnets[0].ids) : toset([])
  id       = each.value
}

data "aws_s3_object" "ui_lambda_package" {
  count  = local.stack_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/dos-ui-server.zip"
}

data "aws_kms_key" "secrets_manager_kms_key" {
  count  = local.stack_enabled
  key_id = local.kms_aliases.secrets_manager
}

data "aws_kms_key" "ssm_kms_key" {
  count  = local.stack_enabled
  key_id = local.kms_aliases.ssm
}

data "aws_iam_role" "app_github_runner_iam_role" {
  count = local.stack_enabled
  name  = "${var.repo_name}-${var.environment}-${var.app_github_runner_role_name}"
}

data "aws_ssm_parameter" "dos_aws_account_id_mgmt" {
  count = local.stack_enabled
  name  = "/dos/${var.environment}/aws_account_id_mgmt"
}

data "aws_iam_policy_document" "secrets_access_policy" {
  count = local.stack_enabled
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = concat(
      [
        "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:/${var.project}/${var.environment}/cis2-private-key*",
        "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:/${var.project}/${var.environment}/cis2-public-key*",
      ],
      [aws_secretsmanager_secret.session_secret[0].arn]
    )
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = [
      data.aws_kms_key.secrets_manager_kms_key[0].arn
    ]
  }
}

data "aws_iam_policy_document" "ssm_access_policy" {
  count = local.stack_enabled
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/${local.project_prefix}-crud-apis${local.workspace_suffix}/endpoint",
      "arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter/${var.project}/${var.environment}/cis2-client-config"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:GenerateDataKey"
    ]
    resources = [
      data.aws_kms_key.ssm_kms_key[0].arn
    ]
  }
}

# TODO: FDOS-378 - This is overly permissive and should be resolved when we have control over stack deployment order.
data "aws_iam_policy_document" "execute_api_policy" {
  count = local.stack_enabled
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
  count    = local.stack_enabled
  name     = "${local.project_prefix}-account-wide-${var.waf_name}"
  scope    = var.waf_scope
  provider = aws.us-east-1
}

data "aws_route53_zone" "main" {
  count = local.stack_enabled
  name  = local.env_domain_name
}

data "aws_acm_certificate" "domain_cert" {
  count       = local.stack_enabled
  provider    = aws.us-east-1
  domain      = "*.${local.env_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}

data "aws_iam_policy_document" "dynamodb_session_store_policy" {
  count = local.stack_enabled
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
      module.ui_session_store[0].dynamodb_table_arn,
      "${module.ui_session_store[0].dynamodb_table_arn}/index/*"
    ]
  }
}

data "aws_cloudfront_cache_policy" "caching_disabled" {
  count = local.stack_enabled
  name  = "Managed-CachingDisabled"
}

data "aws_cloudfront_origin_request_policy" "all_viewer_headers" {
  count = local.stack_enabled
  name  = "Managed-AllViewerExceptHostHeader"
}

data "aws_prefix_list" "cloudfront_prefix_list" {
  name     = "com.amazonaws.global.cloudfront.origin-facing"
  provider = aws.us-east-1
}
