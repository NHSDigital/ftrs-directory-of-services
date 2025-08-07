resource "aws_dms_replication_subnet_group" "dms_replication_subnet_group" {
  count = local.deploy_databases ? 1 : 0

  replication_subnet_group_id          = "${local.resource_prefix}-etl-replication-subnet-group"
  replication_subnet_group_description = "Subnet group for DMS ETL replication instance"
  subnet_ids                           = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
}

resource "aws_dms_replication_instance" "dms_replication_instance" {
  count = local.deploy_databases ? 1 : 0

  replication_instance_id     = "${local.resource_prefix}-etl-replication-instance"
  replication_instance_class  = var.dms_replication_instance_class
  allocated_storage           = var.dms_allocated_storage
  vpc_security_group_ids      = [aws_security_group.dms_replication_security_group[0].id]
  replication_subnet_group_id = aws_dms_replication_subnet_group.dms_replication_subnet_group[0].id
  multi_az                    = var.dms_instance_multi_az
}

resource "aws_dms_endpoint" "dms_source_endpoint" {
  count = local.deploy_databases ? 1 : 0

  endpoint_id   = "${local.resource_prefix}-etl-source"
  endpoint_type = "source"
  engine_name   = var.dms_engine
  username      = data.aws_secretsmanager_secret_version.rds_username.secret_string
  password      = data.aws_secretsmanager_secret_version.rds_password.secret_string
  server_name   = module.rds[0].cluster_endpoint
  port          = var.rds_port
  database_name = var.source_rds_database
}

resource "aws_dms_endpoint" "dms_target_endpoint" {
  count = local.deploy_databases ? 1 : 0

  endpoint_id   = "${local.resource_prefix}-etl-target"
  endpoint_type = "target"
  engine_name   = var.dms_engine
  username      = data.aws_secretsmanager_secret_version.rds_username.secret_string
  password      = data.aws_secretsmanager_secret_version.rds_password.secret_string
  server_name   = module.rds_replication_target_db[0].cluster_endpoint
  port          = var.rds_port
  database_name = var.target_rds_database
}

resource "aws_dms_replication_task" "dms_full_replication_task" {
  count = local.deploy_databases ? 1 : 0

  replication_task_id      = "${local.resource_prefix}-etl-full-replication-task"
  migration_type           = var.full_migration_type
  replication_instance_arn = aws_dms_replication_instance.dms_replication_instance[0].replication_instance_arn
  source_endpoint_arn      = aws_dms_endpoint.dms_source_endpoint[0].endpoint_arn
  target_endpoint_arn      = aws_dms_endpoint.dms_target_endpoint[0].endpoint_arn
  table_mappings = templatefile("${path.module}/table-mappings.json", {
    schema_name = var.schema_name
  })

  start_replication_task = true

  replication_task_settings = jsonencode({
    Logging = {
      EnableLogging = var.dms_task_logging_enabled
    }
  })
}

resource "aws_dms_replication_task" "dms_cdc_replication_task" {
  count = local.deploy_databases ? 1 : 0

  replication_task_id      = "${local.resource_prefix}-etl-cdc-replication-task"
  migration_type           = var.cdc_migration_type
  replication_instance_arn = aws_dms_replication_instance.dms_replication_instance[0].replication_instance_arn
  source_endpoint_arn      = aws_dms_endpoint.dms_source_endpoint[0].endpoint_arn
  target_endpoint_arn      = aws_dms_endpoint.dms_target_endpoint[0].endpoint_arn
  table_mappings = templatefile("${path.module}/table-mappings.json", {
    schema_name = var.schema_name
  })

  start_replication_task = false

  replication_task_settings = jsonencode({
    Logging = {
      EnableLogging = var.dms_task_logging_enabled
    }
  })
}
