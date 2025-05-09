variable "application_tag" {
  description = "The version or tag of the etl_ode_code application"
  type        = string
}

variable "commit_hash" {
  description = "The commit hash of the etl ods application"
  type        = string
}

variable "lambda_runtime" {
  description = "The runtime environment for the Lambda function"
}

variable "aws_lambda_layers" {
  description = "A list of Lambda layer ARNs to attach to the Lambda function"
  type        = list(string)
}

variable "extract_name" {
  description = "The name of the ETL ODS Extract Lambda function"
}

variable "processor_lambda_connection_timeout" {
  description = "The timeout for the ETL ODS Extract Lambda function"
  type        = number
}

variable "processor_lambda_memory_size" {
  description = "The memory size for the ETL ODS Extract Lambda function"
  type        = number
}

variable "processor_lambda_handler" {
  description = "The handler for the ETL ODS Extract Lambda function"
  type        = string
}

variable "data_migration_rds_min_capacity" {
  description = "The minimum capacity for the RDS instance"
  type        = number
}

variable "data_migration_rds_max_capacity" {
  description = "The maximum capacity for the RDS instance"
  type        = number
}

variable "etl_ods_pipeline_store_bucket_name" {
  description = "The name of the S3 bucket to use for the etl ods pipeline"
}

variable "s3_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
}
