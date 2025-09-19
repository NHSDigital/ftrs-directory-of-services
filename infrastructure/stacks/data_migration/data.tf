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

data "aws_security_group" "vpce_rds_security_group" {
  name = "${local.account_prefix}-current-dos-rds-vpc-endpoint-sg"
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

data "aws_iam_policy_document" "secrets_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:/${var.project}/${var.environment}/${var.source_rds_credentials}-*"
    ]
  }
}

data "aws_iam_policy_document" "secrets_access_policy_for_dms" {
  count = local.is_primary_environment ? 1 : 0
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:/${var.project}/${var.environment}/${var.target_rds_credentials}-*",
      "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:/${var.project}/${var.environment}/${var.dms_user_password}-*"
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
      aws_sqs_queue.dms_event_queue.arn
    ]
  }
}

data "aws_iam_policy_document" "lambda_rds_policy" {
  count = local.is_primary_environment ? 1 : 0
  statement {
    effect = "Allow"
    actions = [
      "rds:DescribeDBInstances",
      "rds:DescribeDBClusters",
      "rds:ExecuteStatement",
      "rds-data:ExecuteStatement",
      "rds-data:BatchExecuteStatement",
      "rds-data:BeginTransaction",
      "rds-data:CommitTransaction",
      "rds-data:RollbackTransaction"
    ]
    resources = [
      module.rds_replication_target_db[0].cluster_arn
    ]
  }
}

data "aws_iam_policy_document" "rds_event_listener_sqs_access_policy" {
  count = local.is_primary_environment ? 1 : 0
  statement {
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [
      "${aws_sqs_queue.dms_event_queue.arn}*"
    ]
  }
}

data "aws_iam_policy_document" "ssm_access_policy" {
  count = local.is_primary_environment ? 1 : 0
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = ["arn:aws:ssm:${var.aws_region}:${local.account_id}:parameter${var.sqs_ssm_path_for_ids}${var.environment}/*"]
  }
}

data "aws_iam_policy_document" "rds_connect_policy" {
  count = local.is_primary_environment ? 1 : 0
  statement {
    effect = "Allow"
    actions = [
      "rds-db:connect"
    ]
    resources = [
      "arn:aws:rds-db:${var.aws_region}:${local.account_id}:dbuser:${module.rds_replication_target_db[0].cluster_id}/${aws_secretsmanager_secret_version.rds_username[0].secret_string}"
    ]
  }
}

data "aws_prefix_list" "dynamodb" {
  name = "com.amazonaws.${var.aws_region}.dynamodb"
}
