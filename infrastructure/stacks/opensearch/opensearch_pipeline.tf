resource "aws_osis_pipeline" "dynamodb_to_opensearch_osis_pipeline" {
  for_each = data.aws_dynamodb_table.dynamodb_tables

  pipeline_name = "${each.key}${local.workspace_suffix}"
  min_units     = var.osis_pipeline_min_units
  max_units     = var.osis_pipeline_max_units

  log_publishing_options {
    cloudwatch_log_destination {
      log_group = aws_cloudwatch_log_group.osis_pipeline_cloudwatch_log_group.name
    }
    is_logging_enabled = true
  }

  vpc_options {
    subnet_ids         = data.aws_subnets.private_subnets.ids
    security_group_ids = [aws_security_group.opensearch_security_group.id]
  }

  buffer_options {
    persistent_buffer_enabled = var.osis_pipeline_persistent_buffer_enabled
  }

  pipeline_configuration_body = templatefile("pipeline-config.yaml.tmpl", {
    dynamodb_table_arn  = each.value.arn
    role_arn            = aws_iam_role.osis_pipelines_role.arn
    region              = var.aws_region
    opensearch_endpoint = module.opensearch_serverless.endpoint
    index_name          = each.value.name
    s3_bucket           = module.s3.s3_bucket_id
    s3_prefix           = var.ddb_export_s3_prefix
    network_policy_name = "${var.project}${local.workspace_suffix}-private"
  })
}

resource "aws_cloudwatch_log_group" "osis_pipeline_cloudwatch_log_group" {
  name              = "/aws/vendedlogs/OpenSearchIngestion/dynamodb-to-os${local.workspace_suffix}"
  retention_in_days = var.osis_pipeline_log_retention_in_days
}
