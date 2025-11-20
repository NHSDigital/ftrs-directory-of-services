resource "aws_secretsmanager_secret" "rds_username" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count = local.is_primary_environment ? 1 : 0

  name = "${var.project}/${var.environment}/rds-username"
}

resource "aws_secretsmanager_secret_version" "rds_username" {
  count = local.is_primary_environment ? 1 : 0

  secret_id     = aws_secretsmanager_secret.rds_username[0].id
  secret_string = random_pet.rds_username[0].id
}

resource "aws_secretsmanager_secret" "rds_password" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count = local.is_primary_environment ? 1 : 0

  name = "${var.project}/${var.environment}/rds-password"
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  count = local.is_primary_environment ? 1 : 0

  secret_id     = aws_secretsmanager_secret.rds_password[0].id
  secret_string = random_password.rds_password[0].result
}

resource "random_id" "dms_user_password_suffix" {
  count       = local.is_primary_environment ? 1 : 0
  byte_length = 5
}

resource "aws_secretsmanager_secret" "dms_user_password" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count = local.is_primary_environment ? 1 : 0

  name = "/${var.project}/${var.environment}/${var.dms_user_password}-${random_id.dms_user_password_suffix[0].hex}"
}

resource "aws_secretsmanager_secret_version" "dms_user_password" {
  count = local.is_primary_environment ? 1 : 0

  secret_id     = aws_secretsmanager_secret.dms_user_password[0].id
  secret_string = random_password.dms_user_password[0].result
}

resource "random_password" "dms_user_password" {
  count = local.is_primary_environment ? 1 : 0

  length  = 16
  special = false
  upper   = true
  lower   = true
}

resource "aws_secretsmanager_secret" "source_rds_credentials" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count = local.is_primary_environment ? 1 : 0

  name = "/${var.project}/${var.environment}/${var.source_rds_credentials}"
}

resource "aws_secretsmanager_secret_version" "source_rds_credentials" {
  count = local.is_primary_environment ? 1 : 0

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
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count = local.is_primary_environment ? 1 : 0

  name = "/${var.project}/${var.environment}/${var.target_rds_credentials}"
}

resource "aws_secretsmanager_secret_version" "target_rds_credentials" {
  count = local.is_primary_environment ? 1 : 0

  secret_id = aws_secretsmanager_secret.target_rds_credentials[0].id
  secret_string = jsonencode({
    host     = module.rds_replication_target_db[0].cluster_endpoint,
    port     = var.rds_port,
    username = aws_secretsmanager_secret_version.rds_username[0].secret_string,
    password = aws_secretsmanager_secret_version.rds_password[0].secret_string,
    dbname   = var.target_rds_database
  })
}

resource "aws_secretsmanager_secret" "replica_rds_credentials" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count = local.is_primary_environment ? 1 : 0

  name = "/${var.project}/${var.environment}/${var.replica_rds_credentials}"
}

resource "aws_secretsmanager_secret_version" "replica_rds_credentials" {
  count = local.is_primary_environment ? 1 : 0

  secret_id = aws_secretsmanager_secret.replica_rds_credentials[0].id
  secret_string = jsonencode({
    host     = module.rds_replication_target_db[0].cluster_endpoint,
    port     = var.rds_port,
    username = aws_secretsmanager_secret_version.rds_username[0].secret_string,
    password = aws_secretsmanager_secret_version.rds_password[0].secret_string,
    dbname   = var.replica_rds_database
  })
}
