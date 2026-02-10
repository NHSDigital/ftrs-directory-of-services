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

data "aws_lambda_function" "dynamodb_lambda_connector" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  function_name = "${local.resource_prefix}-dynamodb-connector"
  depends_on    = [aws_serverlessapplicationrepository_cloudformation_stack.dynamodb_connector]
}

data "aws_lambda_function" "rds_lambda_connector" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  function_name = "${local.resource_prefix}-rds-connector"
  depends_on    = [aws_serverlessapplicationrepository_cloudformation_stack.rds_connector]
}

data "aws_security_group" "dms_replication_security_group" {
  name = "${local.project_prefix}-account-wide-etl-replication-sg"
}

data "aws_secretsmanager_secret" "target_rds_credentials" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  name  = "/${var.project}/${var.environment}/${var.target_rds_credentials}"
}

data "aws_secretsmanager_secret_version" "target_rds_credentials" {
  count     = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  secret_id = data.aws_secretsmanager_secret.target_rds_credentials[0].id
}

data "aws_kms_key" "s3_kms_key" {
  count  = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  key_id = local.kms_aliases.s3
}

data "aws_kms_key" "athena_kms_key" {
  count  = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  key_id = local.kms_aliases.athena
}
