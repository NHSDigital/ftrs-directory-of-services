opensearch_type                         = "SEARCH"
opensearch_standby_replicas             = "DISABLED"
opensearch_create_access_policy         = true
opensearch_create_network_policy        = false
osis_pipeline_min_units                 = 1
osis_pipeline_max_units                 = 1
osis_pipeline_persistent_buffer_enabled = false
osis_pipeline_log_retention_in_days     = 7
ddb_export_bucket_name                  = "ddb-export"
ddb_export_s3_versioning                = true
ddb_export_s3_prefix                    = "ddb-to-opensearch-export/"
dynamodb_table_names = [
  # "healthcare-service",
  # "location",
  "organisation"
]
