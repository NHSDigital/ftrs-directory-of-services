resource "aws_secretsmanager_secret" "rds_username" {
  count = local.deploy_databases ? 1 : 0

  name = "${var.project}/${var.environment}/rds-username"
}

resource "aws_secretsmanager_secret_version" "rds_username" {
  count = local.deploy_databases ? 1 : 0

  secret_id     = aws_secretsmanager_secret.rds_username[0].id
  secret_string = random_pet.rds_username[0].id
}

resource "aws_secretsmanager_secret" "rds_password" {
  count = local.deploy_databases ? 1 : 0

  name = "${var.project}/${var.environment}/rds-password"
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  count = local.deploy_databases ? 1 : 0

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

//FIXME: Why does this need to be restricted to only dev and test
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
