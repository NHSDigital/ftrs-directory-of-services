osis_pipeline_min_units                 = 1
osis_pipeline_max_units                 = 1
osis_pipeline_persistent_buffer_enabled = false
osis_pipeline_logs_retention_in_days    = 14
ddb_export_bucket_name                  = "ddb-export"
s3_versioning                           = true
ddb_export_s3_prefix                    = "ddb-to-opensearch-export/"
dynamodb_table_names_for_opensearch = [
  "organisation"
]
osis_pipeline_cloudwatch_log_group_name = "/aws/vendedlogs/OpenSearchIngestion/dynamodb-to-os"
max_sink_retries                        = 1
opensearch_pipeline_s3_dlq_bucket_name  = "osis-pipiline-dlq"
opensearch_pipeline_s3_dlq_prefix       = "osis-pipeline-errors/"
