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

variable "location_api_lambda_runtime" {
  description = "The runtime environment for the Lambda function"
}

variable "location_api_lambda_name" {
  description = "The name of the locations api Lambda function"
}

variable "location_api_lambda_timeout" {
  description = "The timeout for the locations api Lambda function"
  type        = number
}

variable "location_api_lambda_memory_size" {
  description = "The memory size for the locations api Lambda function"
  type        = number
}

variable "location_api_lambda_handler" {
  description = "The handler for the locations api Lambda function"
  type        = string
}

variable "crud_apis_store_bucket_name" {
  description = "The name of the S3 bucket to use for the crud apis"
}

variable "s3_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
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

variable "api_gateway_tls_security_policy" {
  description = "The TLS security policy for the API Gateway domain"
  type        = string
  default     = "TLS_1_2"
}

variable "api_gateway_method_cache_enabled" {
  description = "Configure caching at the method level"
  type        = bool
  default     = true
}

variable "api_gateway_method_metrics_enabled" {
  description = "Configure gathering metrics at end point level"
  type        = bool
  default     = true
}

variable "api_gateway_logging_level" {
  description = "The level of logging"
  type        = string
  default     = "INFO"
}

variable "fhir_content_type_header" {
  description = "API Gateway response header mappings for FHIR responses"
  type        = map(string)
  default = {
    "gatewayresponse.header.Content-Type"              = "'application/fhir+json'"
    "gatewayresponse.header.Strict-Transport-Security" = "'max-age=31536000; includeSubDomains'"
    "gatewayresponse.header.X-Content-Type-Options"    = "'nosniff'"
    "gatewayresponse.header.X-Frame-Options"           = "'DENY'"
    "gatewayresponse.header.Cache-Control"             = "'no-store'"
  }
}

variable "gateway_responses" {
  description = "Map of API Gateway gateway_responses with response_type, status_code, and FHIR template"
  type = map(object({
    response_type = string
    status_code   = string
    template      = string
  }))
  default = null
}

variable "crud_api_lambda_logs_retention" {
  description = "The number of days to retain CloudWatch logs for CRUD apis"
  type        = number
  default     = 14
}

variable "vpc_private_subnet_cidr_range" {
  description = "The CIDR range for the VPC private subnets"
  type        = string
  default     = "24"
}

variable "account_wide_stack_name" {
  description = "Stack name used for account-wide resources (used to derive the regional WAF name)"
  type        = string
  default     = "account-wide"
}

variable "regional_waf_name" {
  description = "Base name of the account-wide regional WAF (without prefix)"
  type        = string
  default     = "regional-waf-web-acl"
}
