variable "application_tag" {
  description = "The version or tag of the crud api application"
  type        = string
}

variable "commit_hash" {
  description = "The commit hash of the crud api application"
  type        = string
}

variable "sandbox_lambda_runtime" {
  description = "The runtime environment for the Lambda function"
}

variable "sandbox_lambda_name" {
  description = "The name of the sandbox Lambda function"
}

variable "sandbox_lambda_timeout" {
  description = "The timeout for the sandbox Lambda function"
  type        = number
}

variable "sandbox_lambda_memory_size" {
  description = "The memory size for the sandbox Lambda function"
  type        = number
}

variable "sandbox_lambda_handler" {
  description = "The handler for the sandbox Lambda function"
  type        = string
}

variable "crud_apis_store_bucket_name" {
  description = "The name of the S3 bucket to use for the crud apis"
}

variable "s3_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
}

variable "api_gateway_authorization_type" {
  description = "The authorization type for the API Gateway"
  type        = string
}

variable "api_gateway_payload_format_version" {
  description = "The payload format version for the API Gateway"
  type        = string
}

variable "api_gateway_integration_timeout" {
  description = "The integration timeout for the API Gateway"
  type        = number
}

variable "api_gateway_access_logs_retention_days" {
  description = "The number of days to retain API Gateway access logs"
  type        = number
}

variable "api_gateway_throttling_burst_limit" {
  description = "The burst limit for API Gateway throttling"
  type        = number
}

variable "api_gateway_throttling_rate_limit" {
  description = "The rate limit for API Gateway throttling"
  type        = number
}
