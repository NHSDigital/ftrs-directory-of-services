data "aws_s3_object" "data_migration_lambda_package" {
  count  = local.version_history_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-data-migration-lambda.zip"
}

data "aws_s3_object" "python_dependency_layer" {
  count  = local.version_history_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-data-migration-python-dependency-layer.zip"
}

data "aws_s3_object" "data_layer" {
  count  = local.version_history_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
}

resource "aws_lambda_layer_version" "python_dependency_layer" {
  count               = local.version_history_enabled
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-data-migration-python-dependency-layer.zip"
  s3_object_version = data.aws_s3_object.python_dependency_layer[0].version_id
}

resource "aws_lambda_layer_version" "data_layer" {
  count               = local.version_history_enabled
  layer_name          = "${local.resource_prefix}-data-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common data dependencies for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
  s3_object_version = data.aws_s3_object.data_layer[0].version_id
}

module "version_history" {
  count  = local.version_history_enabled
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
    aws_lambda_layer_version.python_dependency_layer[0].arn,
    aws_lambda_layer_version.data_layer[0].arn
  ]

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.version_history_lambda_security_group[0].id]

  version_history_table_arn = module.dynamodb_tables["version-history"].dynamodb_table_arn

  table_streams = { for table_name in ["organisation", "location", "healthcare-service"] :
    table_name => {
      stream_arn = module.dynamodb_tables[table_name].dynamodb_table_stream_arn
      table_arn  = module.dynamodb_tables[table_name].dynamodb_table_arn
    }
  }

  environment    = var.environment
  workspace      = terraform.workspace == "default" ? "" : terraform.workspace
  project        = var.project
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id
}
