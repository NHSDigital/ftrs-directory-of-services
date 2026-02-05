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

  filter {
    name   = "tag:CidrRange"
    values = [var.vpc_private_subnet_cidr_range]
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}

data "aws_s3_object" "common_packages_layer" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
}

data "aws_s3_object" "python_dependency_layer" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-${var.stack_name}-python-dependency-layer.zip"
}

data "aws_s3_object" "dos_search_lambda_package" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-${var.stack_name}-lambda.zip"
}

data "aws_route53_zone" "dev_ftrs_cloud" {
  name         = local.env_domain_name
  private_zone = false
}
data "aws_acm_certificate" "domain_cert" {
  domain      = "*.${local.env_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}

data "aws_s3_object" "truststore" {
  bucket = local.s3_trust_store_bucket_name
  key    = local.trust_store_file_path
}

data "aws_iam_policy_document" "vpc_access_policy" {
  # checkov:skip=CKV_AWS_111: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-421
  # checkov:skip=CKV_AWS_356: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-421
  statement {
    effect = "Allow"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
    ]
    resources = [
      "*"
    ]
  }
}

data "aws_iam_policy_document" "dynamodb_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
    ]
    resources = flatten([
      for table in local.dynamodb_tables : [
        table.arn,
        "${table.arn}/index/*",
      ]
    ])
  }
}

data "aws_prefix_list" "dynamodb" {
  name = "com.amazonaws.${var.aws_region}.dynamodb"
}

data "aws_security_group" "dos_search_lambda_security_group" {
  count = local.is_primary_environment ? 0 : 1

  name = "${local.resource_prefix}-${var.lambda_name}-sg"
}

# Allow AWS WAF to deliver logs to this account's CloudWatch Log Group.
# WAF requires a CloudWatch Logs resource policy granting delivery.logs.amazonaws.com permission.
# NOTE: data.aws_caller_identity.current is defined in provider.tf for this stack.

data "aws_iam_policy_document" "dos_search_waf_log_group_policy_document" {
  version = "2012-10-17"

  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    actions = ["logs:CreateLogStream", "logs:PutLogEvents"]

    # Match the account_wide approach: allow writing to aws-waf-logs-* log groups in this account/region.
    resources = [
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:aws-waf-logs-${local.resource_prefix}-dos-search${local.workspace_suffix}:log-stream:*"
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
