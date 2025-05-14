variable "osis_pipeline_min_units" {
  description = "The min number of units for the OSIS pipeline"
  type        = number
}

variable "osis_pipeline_max_units" {
  description = "The max number of units for the OSIS pipeline"
  type        = number
}

variable "osis_pipeline_persistent_buffer_enabled" {
  description = "Enable or disable persistent buffer for the OSIS pipeline"
  type        = bool
}

variable "osis_pipeline_log_retention_in_days" {
  description = "The number of days to retain logs for the OSIS pipeline"
  type        = number
}

variable "ddb_export_bucket_name" {
  description = "The name of the DynamoDB export bucket"
  type        = string
}

variable "s3_versioning" {
  description = "Enable versioning for the S3 bucket"
  type        = bool
}

variable "ddb_export_s3_prefix" {
  description = "The prefix to use for S3 bucket paths"
  type        = string
}

variable "dynamodb_table_names_for_opensearch" {
  description = "List of DynamoDB table names"
  type        = list(string)
}

variable "osis_pipeline_cloudwatch_log_group_name" {
  description = "The  cloudwatch log group name for the osis pipeline"
  type        = string
}

variable "max_sink_retries" {
  description = "The number of times OpenSearch Ingestion Service pipeline will retry an action on the sink"
  type        = number
}

variable "opensearch_pipieline_s3_dlq_bucket_name" {
  description = "The DLQ bukcet name for OpenSearch Ingestion Service Pipeline"
  type        = string
}

variable "opensearch_pipieline_s3_dlq_prefix" {
  description = "The DLQ bucket prefix for OpenSearch Ingestion Service Pipeline"
  type        = string
}
