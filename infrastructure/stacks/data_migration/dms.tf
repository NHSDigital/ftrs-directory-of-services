resource "aws_dms_replication_subnet_group" "dms_replication_subnet_group" {
  count = local.is_primary_environment ? 1 : 0

  replication_subnet_group_id          = "${local.resource_prefix}-etl-replication-subnet-group"
  replication_subnet_group_description = "Subnet group for DMS ETL replication instance"
  subnet_ids                           = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
}

resource "aws_dms_replication_instance" "dms_replication_instance" {
  # checkov:skip=CKV_AWS_212: Needs CMK
  count = local.is_primary_environment ? 1 : 0

  replication_instance_id     = "${local.resource_prefix}-etl-replication-instance"
  replication_instance_class  = var.dms_replication_instance_class
  allocated_storage           = var.dms_allocated_storage
  vpc_security_group_ids      = [aws_security_group.dms_replication_security_group[0].id]
  replication_subnet_group_id = aws_dms_replication_subnet_group.dms_replication_subnet_group[0].id
  multi_az                    = var.dms_instance_multi_az
  auto_minor_version_upgrade  = var.dms_replication_instance_auto_minor_version_upgrade
}

resource "aws_dms_endpoint" "dms_source_endpoint" {
  # checkov:skip=CKV_AWS_296: Needs CMK
  count = local.is_primary_environment ? 1 : 0

  endpoint_id   = "${local.resource_prefix}-etl-source"
  endpoint_type = "source"
  engine_name   = var.dms_engine
  ssl_mode      = "require"
  database_name = var.source_rds_database

  secrets_manager_arn             = aws_secretsmanager_secret.source_rds_credentials[0].arn
  secrets_manager_access_role_arn = aws_iam_role.dms_secrets_access[0].arn
}

resource "aws_dms_endpoint" "dms_target_endpoint" {
  # checkov:skip=CKV_AWS_296: Needs CMK
  count = local.is_primary_environment ? 1 : 0

  endpoint_id   = "${local.resource_prefix}-etl-target"
  endpoint_type = "target"
  engine_name   = var.dms_engine
  database_name = var.target_rds_database

  secrets_manager_arn             = aws_secretsmanager_secret.target_rds_credentials[0].arn
  secrets_manager_access_role_arn = aws_iam_role.dms_secrets_access[0].arn
}

resource "aws_dms_replication_task" "dms_full_replication_task" {
  count = local.is_primary_environment ? 1 : 0

  replication_task_id      = "${local.resource_prefix}-etl-full-replication-task"
  migration_type           = var.full_migration_type
  replication_instance_arn = aws_dms_replication_instance.dms_replication_instance[0].replication_instance_arn
  source_endpoint_arn      = aws_dms_endpoint.dms_source_endpoint[0].endpoint_arn
  target_endpoint_arn      = aws_dms_endpoint.dms_target_endpoint[0].endpoint_arn
  table_mappings = templatefile("${path.module}/table-mappings.json", {
    schema_name = var.schema_name
  })

  start_replication_task = var.dms_start_full_replication_task

  replication_task_settings = jsonencode({
    Logging = {
      EnableLogging = var.dms_task_logging_enabled
    },
    FullLoadSettings = {
      TargetTablePrepMode = "DROP_AND_CREATE"
    },
    StopTaskCachedChangesApplied = true
  })
}

resource "aws_dms_replication_task" "dms_cdc_replication_task" {
  count = local.is_primary_environment ? 1 : 0

  replication_task_id      = "${local.resource_prefix}-etl-cdc-replication-task"
  migration_type           = var.cdc_migration_type
  replication_instance_arn = aws_dms_replication_instance.dms_replication_instance[0].replication_instance_arn
  source_endpoint_arn      = aws_dms_endpoint.dms_source_endpoint[0].endpoint_arn
  target_endpoint_arn      = aws_dms_endpoint.dms_target_endpoint[0].endpoint_arn
  table_mappings = templatefile("${path.module}/table-mappings.json", {
    schema_name = var.schema_name
  })

  start_replication_task = var.dms_start_cdc_replication_task

  replication_task_settings = jsonencode({
    Logging = {
      EnableLogging = var.dms_task_logging_enabled
    }
  })
}
