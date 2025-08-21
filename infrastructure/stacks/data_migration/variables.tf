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
variable "dms_replication_instance_class" {
  description = "The instance class for the DMS replication instance"
  type        = string
  default     = null
}

variable "dms_engine" {
  description = "The engine for the DMS replication instance"
  type        = string
  default     = null
}

variable "dms_allocated_storage" {
  description = "The allocated storage for the DMS replication instance"
  type        = number
  default     = null
}

variable "full_migration_type" {
  description = "The type of migration for DMS"
  type        = string
  default     = null
}

variable "cdc_migration_type" {
  description = "The type of migration for DMS"
  type        = string
  default     = null
}

variable "dms_instance_multi_az" {
  description = "Is DMS instance set up in multi-AZ mode"
  type        = bool
  default     = false
}

variable "dms_task_logging_enabled" {
  description = "Enable logging for DMS tasks"
  type        = bool
  default     = true
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

variable "dynamodb_exports_s3_expiration_days" {
  description = "The number of days after which DynamoDB exports in S3 will expire"
  type        = number
}
variable "rds_event_listener_lambda_name" {
  description = "The name of the RDS event listener Lambda function"
  type        = string
}

variable "schema_name" {
  description = "The schema name to use in table mappings"
  type        = string
}

variable "sqs_ssm_path_for_ids" {
  description = "The SSM path for storing SQS IDs"
  type        = string
}

variable "migration_copy_db_lambda_trigger" {
  description = "The Lambda function handler for the migration copy DB trigger"
  type        = string
}

variable "cloudwatch_log_retention_days" {
  description = "The number of days to retain CloudWatch logs for DMS tasks"
  type        = number
}

variable "dms_db_lambda_name" {
  description = "The name of the DMS DB setup Lambda function"
  type        = string
}

variable "dms_db_lambda_trigger" {
  description = "The Lambda function handler for the DMS DB setup trigger"
  type        = string
}

variable "dms_start_full_replication_task" {
  description = "Whether to start the DMS replication task automatically"
  type        = bool
  default     = false
}

variable "dms_start_cdc_replication_task" {
  description = "Whether to start the DMS replication task automatically"
  type        = bool
  default     = false
}

variable "dms_replication_instance_auto_minor_version_upgrade" {
  description = "Whether to enable auto minor version upgrades for the DMS replication instance"
  type        = bool
  default     = true
}

variable "rds_event_listener_lambda_connection_timeout" {
  description = "The connection timeout for the RDS event listener Lambda function"
  type        = number
}

variable "rds_event_listener_lambda_memory_size" {
  description = "The memory size for the RDS event listener Lambda function"
  type        = number
}

variable "dms_db_lambda_connection_timeout" {
  description = "The connection timeout for the DMS DB setup Lambda function"
  type        = number
}

variable "dms_db_lambda_memory_size" {
  description = "The memory size for the DMS DB setup Lambda function"
  type        = number
}

variable "full_migration_completion_event_queue_name" {
  description = "The name of the SQS queue for full migration completion events"
  type        = string
}

variable "target_rds_credentials" {
  description = "The secrets manager name for the target RDS details"
  type        = string
}

variable "dms_user_password" {
  description = "The secrets manager name for the DMS user password"
  type        = string
}

variable "source_rds_credentials" {
  description = "The secrets manager name for the source RDS credentials"
  type        = string
}

variable "dns_port" {
  description = "The port for DNS queries"
  type        = number
  default     = 53
}

variable "https_port" {
  description = "The port for HTTPS traffic"
  type        = number
  default     = 443
}
