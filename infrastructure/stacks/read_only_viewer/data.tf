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

data "aws_s3_object" "read_only_viewer_lambda_package" {
  count  = local.stack_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/read-only-viewer-server.zip"
}

data "aws_iam_role" "app_github_runner_iam_role" {
  count = local.stack_enabled
  name  = "${var.repo_name}-${var.environment}-${var.app_github_runner_role_name}"
}

data "aws_ssm_parameter" "dos_aws_account_id_mgmt" {
  count = local.stack_enabled
  name  = "/dos/${var.environment}/aws_account_id_mgmt"
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
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${local.project_prefix}-crud-apis${local.workspace_suffix}/endpoint"
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

data "aws_ec2_managed_prefix_list" "cloudfront_prefix_list" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}
