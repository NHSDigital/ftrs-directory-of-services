resource "random_pet" "rds_username" {
  count = local.deploy_databases ? 1 : 0

  length    = 2
  separator = "_"
}

resource "random_password" "rds_password" {
  count = local.deploy_databases ? 1 : 0

  length  = 16
  special = false
  upper   = true
  lower   = true
}

module "rds" {
  count   = local.deploy_databases ? 1 : 0
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "9.10.0"

  name           = "${local.prefix}-rds"
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
  database_name               = var.rds_database

  iam_database_authentication_enabled = true

  create_db_subnet_group = false
  create_security_group  = false
  vpc_id                 = data.aws_vpc.vpc.id
  db_subnet_group_name   = "${var.main_project}-${var.environment}-database-subnet-group"
  vpc_security_group_ids = [aws_security_group.rds_security_group[0].id]

  final_snapshot_identifier = "${local.prefix}-rds"
}

resource "aws_secretsmanager_secret" "rds_username" {
  count = local.deploy_databases ? 1 : 0

  name = "${var.project}/${var.environment}/rds_username"
}

resource "aws_secretsmanager_secret_version" "rds_username" {
  count = local.deploy_databases ? 1 : 0

  secret_id     = aws_secretsmanager_secret.rds_username[0].id
  secret_string = random_pet.rds_username[0].id
}

resource "aws_secretsmanager_secret" "rds_password" {
  count = local.deploy_databases ? 1 : 0

  name = "${var.project}/${var.environment}/rds_password"
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  count = local.deploy_databases ? 1 : 0

  secret_id     = aws_secretsmanager_secret.rds_password[0].id
  secret_string = random_password.rds_password[0].result
}

resource "aws_ssm_parameter" "rds_database_uri" {
  count = local.deploy_databases ? 1 : 0

  name  = "/${var.project}/${var.environment}/rds-uri"
  type  = "SecureString"
  value = "postgres://${random_pet.rds_username[0].id}:${random_password.rds_password[0].result}@${module.rds[0].cluster_endpoint}:${module.rds[0].cluster_port}/${var.rds_database}"
}

resource "null_resource" "rds_schema_creation" {
  depends_on = [module.rds]
  count      = local.deploy_databases ? 1 : 0

  # Use a trigger to force re-execution when the SQL file changes.
  # triggers = {
  #   schema_hash = filesha256("${path.module}/../../../services/data-migration/schema/target-state.sql")
  # }

  provisioner "local-exec" {
    command = <<-EOT
    cd "${path.module}/../../../services/data-migration" && \
    curl -sSL https://install.python-poetry.org | python && \
    export PATH="$HOME/.local/bin:$PATH" && \
    poetry install && \
    poetry run python -m pipeline.schema \
      --db-uri "${aws_ssm_parameter.rds_database_uri[0].value}" \
      --schema-path "schema/target-state.sql"
  EOT
  }
}
