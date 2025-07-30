data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_ec2_client_vpn_endpoint" "client_vpn_endpoint" {
  count = var.environment == "dev" ? 1 : 0
  filter {
    name   = "tag:Project"
    values = ["${var.project}"]
  }
}

data "aws_security_group" "vpn_security_group" {
  count = var.environment == "dev" ? 1 : 0
  name  = "${local.account_prefix}-vpn-sg"
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

data "aws_iam_policy_document" "s3_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:HeadBucket",
      "s3:ListBucket"
    ]
    resources = [
      module.migration_store_bucket.s3_bucket_arn,
      "${module.migration_store_bucket.s3_bucket_arn}/*",
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
      "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:/${var.project}/${var.environment}/source-rds-credentials-*"
    ]
  }
}

data "aws_iam_policy_document" "dynamodb_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem"
    ]
    resources = flatten([
      for table in local.dynamodb_tables : [
        table.arn,
        "${table.arn}/index/*"
      ]
    ])
  }
}

data "aws_iam_policy_document" "sqs_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
    resources = [
      aws_sqs_queue.rds_event_listener.arn
    ]
  }
}
