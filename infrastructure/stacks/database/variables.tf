variable "dynamodb_tables" {
  description = "List of DynamoDB tables"
  type = map(object({
    hash_key  = string
    range_key = string
    attributes = list(object({
      name = string
      type = string
    }))
    global_secondary_indexes = optional(list(object({
      name               = string
      hash_key           = string
      range_key          = optional(string)
      projection_type    = string
      non_key_attributes = optional(list(string))
    })))
  }))
}

variable "version_history_lambda_runtime" {
  description = "The runtime for the Lambda functions"
  type        = string
}

variable "version_history_lambda_name" {
  description = "The name of the version history Lambda function"
  type        = string
}

variable "version_history_lambda_handler" {
  description = "The handler for the version history Lambda function"
  type        = string
}

variable "version_history_lambda_timeout" {
  description = "The timeout for the version history Lambda function"
  type        = number
}

variable "version_history_lambda_memory_size" {
  description = "The memory size for the version history Lambda function"
  type        = number
}

variable "version_history_lambda_logs_retention" {
  description = "The logs retention for the version history Lambda function"
  type        = number
  default     = 14
}

variable "version_history_batch_size" {
  description = "The batch size for DynamoDB stream event source mappings"
  type        = number
}

variable "version_history_maximum_concurrency" {
  description = "The maximum concurrency for DynamoDB stream event source mappings"
  type        = number
}
