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

data "aws_security_group" "dms_replication_security_group" {
  name = "${var.project}-${var.environment}-*-etl-replication-sg"
}

data "aws_lambda_function" "dynamodb_lambda_connector" {
  function_name = "${local.resource_prefix}-dynamodb-connector"
  depends_on    = [aws_serverlessapplicationrepository_cloudformation_stack.dynamodb_connector]
}

data "aws_secretsmanager_secret_version" "replica_rds" {
  name = "/${var.project}/${var.environment}/${var.replica_rds_credentials}"
}

data "aws_secretsmanager_secret_version" "replica_rds" {
  secret_id = data.aws_secretsmanager_secret.replica_rds.id
}
