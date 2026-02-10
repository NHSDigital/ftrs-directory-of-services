data "aws_s3_object" "data_migration_lambda_package" {
  count  = var.version_history_enabled ? 1 : 0
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-data-migration-lambda.zip"
}

data "aws_lambda_layer_version" "python_dependency_layer" {
  count      = var.version_history_enabled ? 1 : 0
  layer_name = "${local.resource_prefix}-python-dependency-layer"
}

data "aws_lambda_layer_version" "data_layer" {
  count      = var.version_history_enabled ? 1 : 0
  layer_name = "${local.resource_prefix}-data-layer"
}

module "version_history" {
  count  = var.version_history_enabled ? 1 : 0
  source = "../../modules/version_history"

  resource_prefix       = local.resource_prefix
  lambda_name           = var.version_history_lambda_name
  lambda_handler        = var.version_history_lambda_handler
  lambda_runtime        = var.lambda_runtime
  lambda_timeout        = var.version_history_lambda_timeout
  lambda_memory_size    = var.version_history_lambda_memory_size
  lambda_logs_retention = var.version_history_lambda_logs_retention
  batch_size            = var.version_history_batch_size
  maximum_concurrency   = var.version_history_maximum_concurrency

  artefacts_bucket         = local.artefacts_bucket
  lambda_s3_key            = "${local.artefact_base_path}/${var.project}-data-migration-lambda.zip"
  lambda_s3_key_version_id = data.aws_s3_object.data_migration_lambda_package[0].version_id

  lambda_layers = [
    data.aws_lambda_layer_version.python_dependency_layer[0].arn,
    data.aws_lambda_layer_version.data_layer[0].arn
  ]

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [data.aws_security_group.processor_lambda_security_group[0].id]

  version_history_table_name = "${local.project_prefix}-database-version-history${local.workspace_suffix}"
  version_history_table_arn  = module.version_history_table[0].dynamodb_table_arn

  organisation_stream_arn       = module.dynamodb_tables["organisation"].dynamodb_table_stream_arn
  location_stream_arn           = module.dynamodb_tables["location"].dynamodb_table_stream_arn
  healthcare_service_stream_arn = module.dynamodb_tables["healthcare-service"].dynamodb_table_stream_arn

  organisation_table_arn       = module.dynamodb_tables["organisation"].dynamodb_table_arn
  location_table_arn           = module.dynamodb_tables["location"].dynamodb_table_arn
  healthcare_service_table_arn = module.dynamodb_tables["healthcare-service"].dynamodb_table_arn

  kms_key_arn = data.aws_kms_key.secrets_manager_kms_key.arn

  environment    = var.environment
  workspace      = terraform.workspace == "default" ? "" : terraform.workspace
  project        = var.project
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id
}
