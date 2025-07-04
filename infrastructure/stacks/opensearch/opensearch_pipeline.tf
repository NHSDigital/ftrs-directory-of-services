resource "aws_osis_pipeline" "dynamodb_to_opensearch_osis_pipeline" {
  for_each = toset(var.dynamodb_table_names_for_opensearch)

  pipeline_name = "${var.environment}-${each.value}${local.workspace_suffix}"
  min_units     = var.osis_pipeline_min_units
  max_units     = var.osis_pipeline_max_units

  log_publishing_options {
    cloudwatch_log_destination {
      log_group = aws_cloudwatch_log_group.osis_pipeline_cloudwatch_log_group.name
    }
    is_logging_enabled = true
  }

  buffer_options {
    persistent_buffer_enabled = var.osis_pipeline_persistent_buffer_enabled
  }

  pipeline_configuration_body = templatefile("pipeline-config.yaml.tmpl", {
    dynamodb_table_arn   = "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/${var.project}-${var.environment}-database-${each.value}${local.workspace_suffix}"
    role_arn             = aws_iam_role.osis_pipelines_role.arn
    region               = var.aws_region
    opensearch_endpoint  = data.aws_opensearchserverless_collection.opensearch_serverless_collection.collection_endpoint
    index_name           = "${each.value}${local.workspace_suffix}"
    s3_bucket            = module.s3.s3_bucket_id
    s3_prefix            = var.ddb_export_s3_prefix
    network_policy_name  = "pipeline-${aws_opensearchserverless_security_policy.opensearch_serverless_network_access_policy.name}"
    max_sink_retries     = var.max_sink_retries
    s3_dlq_bucket        = module.s3_opensearch_pipeline_dlq_bucket.s3_bucket_id
    s3_dlq_bucket_prefix = var.opensearch_pipeline_s3_dlq_prefix
  })
}
