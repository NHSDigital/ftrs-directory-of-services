resource "random_pet" "rds_username" {
  count = local.deploy_databases && local.rds_environments ? 1 : 0

  length    = 2
  separator = "_"
}

resource "random_password" "rds_password" {
  count = local.deploy_databases && local.rds_environments ? 1 : 0

  length  = 16
  special = false
  upper   = true
  lower   = true
}

module "rds" {
  count = local.deploy_databases && local.rds_environments ? 1 : 0
  # Module version: 9.13.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-rds-aurora.git?ref=592cb15809bde8eed2a641ba5971ec665c9b4397"

  name           = "${local.resource_prefix}-rds"
  engine         = var.rds_engine
  engine_version = var.rds_engine_version
  engine_mode    = var.rds_engine_mode
  port           = var.rds_port

  instance_class = var.rds_instance_class
  instances = {
    one = {}
  }

  serverlessv2_scaling_configuration = {
    min_capacity = var.data_migration_rds_min_capacity
    max_capacity = var.data_migration_rds_max_capacity
  }

  manage_master_user_password = false
  master_username             = random_pet.rds_username[0].id
  master_password             = random_password.rds_password[0].result
  database_name               = var.source_rds_database

  iam_database_authentication_enabled = true

  create_db_subnet_group = false
  create_security_group  = false
  vpc_id                 = data.aws_vpc.vpc.id
  db_subnet_group_name   = "${local.account_prefix}-database-subnet-group"
  vpc_security_group_ids = [aws_security_group.rds_security_group[0].id]

  final_snapshot_identifier = "${local.resource_prefix}-rds"

  deletion_protection = true
}

resource "aws_secretsmanager_secret" "rds_username" {
  count = local.deploy_databases && local.rds_environments ? 1 : 0

  name = "${var.project}/${var.environment}/rds-username"
}

resource "aws_secretsmanager_secret_version" "rds_username" {
  count = local.deploy_databases && local.rds_environments ? 1 : 0

  secret_id     = aws_secretsmanager_secret.rds_username[0].id
  secret_string = random_pet.rds_username[0].id
}

resource "aws_secretsmanager_secret" "rds_password" {
  count = local.deploy_databases && local.rds_environments ? 1 : 0

  name = "${var.project}/${var.environment}/rds-password"
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  count = local.deploy_databases && local.rds_environments ? 1 : 0

  secret_id     = aws_secretsmanager_secret.rds_password[0].id
  secret_string = random_password.rds_password[0].result
}

resource "aws_secretsmanager_secret" "source_rds_credentials" {
  count = local.deploy_databases ? 1 : 0

  name = "/${var.project}/${var.environment}/source-rds-credentials"
}

resource "aws_secretsmanager_secret_version" "source_rds_credentials" {
  count = local.deploy_databases ? 1 : 0

  secret_id = aws_secretsmanager_secret.source_rds_credentials[0].id
  secret_string = jsonencode({
    host     = "NOT_SET",
    port     = var.rds_port,
    username = "NOT_SET",
    password = "NOT_SET",
    dbname   = var.source_rds_database
  })
}

resource "aws_secretsmanager_secret" "target_rds_credentials" {
  count = local.deploy_databases ? 1 : 0

  name = "/${var.project}/${var.environment}/target-rds-credentials"
}

resource "aws_secretsmanager_secret_version" "target_rds_credentials" {
  count = local.deploy_databases ? 1 : 0

  secret_id = aws_secretsmanager_secret.target_rds_credentials[0].id
  secret_string = jsonencode({
    host     = "NOT_SET",
    port     = var.rds_port,
    username = "NOT_SET",
    password = "NOT_SET",
    dbname   = var.target_rds_database
  })
}
