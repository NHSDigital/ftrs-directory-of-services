variable "athena_spill_bucket_retention_days" {
  description = "The retention period for the Athena spill bucket"
  type        = number
  default     = 1
}

variable "athena_output_bucket_retention_days" {
  description = "The retention period for the Athena output bucket"
  type        = number
  default     = 30
}

variable "athena_postgres_connector_app_id" {
  description = "SAR application ID for the Athena PostgreSQL Connector"
  type        = string
  default     = "arn:aws:serverlessrepo:us-east-1:292517598671:applications/AthenaPostgreSQLConnector"
}

variable "athena_dynamodb_connector_app_id" {
  description = "SAR application ID for the Athena DynamoDB Connector"
  type        = string
  default     = "arn:aws:serverlessrepo:us-east-1:292517598671:applications/AthenaDynamoDBConnector"
}

variable "target_rds_credentials" {
  description = "The secrets manager name for the target RDS credentials"
  type        = string
  default     = "target-rds-credentials"
}
