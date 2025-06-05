variable "application_tag" {
  description = "The version or tag of the crud api application"
  type        = string
}

variable "commit_hash" {
  description = "The commit hash of the crud api application"
  type        = string
}

variable "organisation_api_lambda_runtime" {
  description = "The runtime environment for the Lambda function"
}

variable "organisation_api_lambda_name" {
  description = "The name of the organisations api Lambda function"
}

variable "organisation_api_lambda_timeout" {
  description = "The timeout for the organisations api Lambda function"
  type        = number
}

variable "organisation_api_lambda_memory_size" {
  description = "The memory size for the organisations api Lambda function"
  type        = number
}

variable "organisation_api_lambda_handler" {
  description = "The handler for the organisations api Lambda function"
  type        = string
}

variable "healthcare_service_api_lambda_runtime" {
  description = "The runtime environment for the Lambda function"
}

variable "healthcare_service_api_lambda_name" {
  description = "The name of the healthcare services api Lambda function"
}

variable "healthcare_service_api_lambda_timeout" {
  description = "The timeout for the healthcare services api Lambda function"
  type        = number
}

variable "healthcare_service_api_lambda_memory_size" {
  description = "The memory size for the healthcare services api Lambda function"
  type        = number
}

variable "healthcare_service_api_lambda_handler" {
  description = "The handler for the healthcare services api Lambda function"
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

variable "api_gateway_access_log_retention_days" {
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
