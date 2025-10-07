variable "gp_search_service_name" {
  description = "The name of the gp search service"
}
variable "s3_bucket_name" {
  description = "The name of the gp search bucket"
}
variable "lambda_name" {
  description = "The name of the gp search lambda"
}
variable "health_check_lambda_name" {
  description = "The name of the health check lambda for gp search"
}
variable "lambda_runtime" {
  description = "The runtime environment for the lambda function"
}
variable "lambda_memory_size" {
  description = "The memory size of the lambda function"
  type        = number
}
variable "lambda_timeout" {
  description = "The connection timeout of the lambda function"
  type        = number
}
variable "application_tag" {
  description = "The version or tag of the gp search application"
  type        = string
  default     = "latest"
}
variable "commit_hash" {
  description = "The commit hash of the gp search application"
  type        = string
}
variable "api_gateway_access_logs_retention_days" {
  description = "The retention period in days for API Gateway logging"
  type        = number
  default     = 7
}

variable "api_gateway_payload_format_version" {
  description = "The version of the payload format"
  type        = string
  default     = "2.0"
}

variable "api_gateway_integration_timeout" {
  description = "Timeout to integration ARN"
  type        = number
}

variable "lambda_cloudwatch_logs_retention_days" {
  description = "Number of days to retain CloudWatch logs for the main search Lambda"
  type        = number
  default     = 30
}

variable "health_check_lambda_cloudwatch_logs_retention_days" {
  description = "Number of days to retain CloudWatch logs for the health check Lambda"
  type        = number
  default     = 7
}
