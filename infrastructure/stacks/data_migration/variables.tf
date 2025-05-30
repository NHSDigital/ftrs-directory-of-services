variable "application_tag" {
  description = "The version or tag of the data migration application"
  type        = string
}

variable "commit_hash" {
  description = "The commit hash of the data migration application"
  type        = string
}

variable "migration_pipeline_store_bucket_name" {
  description = "The name of the S3 bucket to use for the data migration pipeline"
}

variable "s3_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
}

variable "target_rds_database" {
  description = "The name of the target RDS database"
  type        = string
}

variable "source_rds_database" {
  description = "The name of the source RDS database"
  type        = string
}

variable "rds_port" {
  description = "The port RDS will listen on"
  type        = string
}

variable "rds_engine" {
  description = "The engine for the RDS instance"
  type        = string
}

variable "rds_engine_version" {
  description = "The engine version for the RDS instance"
  type        = string
}

variable "rds_engine_mode" {
  description = "The engine mode for the RDS instance"
  type        = string
}

variable "rds_instance_class" {
  description = "The instance class for the RDS instance"
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

variable "lambda_runtime" {
  description = "The runtime environment for the Lambda function"
}

variable "aws_lambda_layers" {
  description = "A list of Lambda layer ARNs to attach to the Lambda function"
  type        = list(string)
}

variable "extract_name" {
  description = "The extract name of the Lambda function"
}

variable "extract_lambda_connection_timeout" {
  description = "The timeout for the extract Lambda function"
  type        = number
}

variable "extract_lambda_memory_size" {
  description = "The memory size for the extract Lambda function"
  type        = number
}

variable "extract_lambda_handler" {
  description = "The handler for the extract Lambda function"
  type        = string
}

variable "transform_name" {
  description = "The transform name of the Lambda function"
}

variable "transform_lambda_connection_timeout" {
  description = "The timeout for the transform Lambda function"
  type        = number
}

variable "transform_lambda_memory_size" {
  description = "The memory size for the transform Lambda function"
  type        = number
}

variable "transform_lambda_handler" {
  description = "The handler for the transform Lambda function"
  type        = string
}

variable "data_collection_date" {
  description = "The date the data has been collected"
  type        = string
}

variable "load_name" {
  description = "The load name of the Lambda function"
}

variable "load_lambda_connection_timeout" {
  description = "The timeout for the load Lambda function"
  type        = number
}

variable "load_lambda_memory_size" {
  description = "The memory size for the load Lambda function"
  type        = number
}

variable "load_lambda_handler" {
  description = "The handler for the load Lambda function"
  type        = string
}
