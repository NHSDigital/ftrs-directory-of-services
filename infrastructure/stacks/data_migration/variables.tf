variable "main_project" {
  description = "The name of the main project"
}

variable "application_tag" {
  description = "The version or tag of the data mirgation application"
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
