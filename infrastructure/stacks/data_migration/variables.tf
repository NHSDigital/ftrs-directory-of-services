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

variable "processor_lambda_name" {
  description = "The name of the processor lambda function"
}

variable "processor_lambda_timeout" {
  description = "The timeout for the processor Lambda function"
  type        = number
}

variable "processor_lambda_memory_size" {
  description = "The memory size for the processor Lambda function"
  type        = number
}

variable "processor_lambda_handler" {
  description = "The handler for the processor Lambda function"
  type        = string
}

variable "dms_event_queue_name" {
  description = "The name of the DMS event queue"
  type        = string
}

variable "dms_event_queue_enabled" {
  description = "Flag to enable the DMS event queue"
  type        = bool
  default     = true
}

variable "dms_event_queue_batch_size" {
  description = "The batch size for the DMS event queue"
  type        = number
  default     = 50
}

variable "dms_event_queue_maximum_batching_window_in_seconds" {
  description = "The maximum batching window in seconds for the DMS event queue"
  type        = number
  default     = 1
}

variable "dms_event_queue_maximum_concurrency" {
  description = "The maximum concurrency for the DMS event queue"
  type        = number
  default     = 20
}

variable "queue_populator_lambda_name" {
  description = "The name of the queue populator lambda function"
}

variable "queue_populator_lambda_timeout" {
  description = "The timeout for the queue populator Lambda function"
  type        = number
}

variable "queue_populator_lambda_memory_size" {
  description = "The memory size for the queue populator Lambda function"
  type        = number
}

variable "queue_populator_lambda_handler" {
  description = "The handler for the queue populator Lambda function"
  type        = string
}

variable "data_collection_date" {
  description = "The date the data has been collected"
  type        = string
}
