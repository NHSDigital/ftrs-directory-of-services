variable "dos_search_service_name" {
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

variable "vpc_private_subnet_cidr_range" {
  description = "The CIDR range for the VPC private subnets"
  type        = string
  default     = "24"
}

#####################################################

# API Gateway

variable "api_gateway_name" {
  description = "The name of the API Gateway"
  default     = "default"
}

variable "api_gateway_description" {
  description = "The description of the API Gateway"
  default     = "DoS Search API"
}

variable "api_gateway_log_group_class" {
  description = "The logging group class of the API Gateway log group"
  default     = "STANDARD"
}

variable "api_gateway_log_group_retention_days" {
  description = "The period of time in days to retain logs for the API Gateway log group"
  default     = "7"
}

variable "api_gateway_xray_tracing" {
  description = "Flag to enable or disable xray tracing at the API Gateway"
  default     = true
}

variable "api_gateway_logging_level" {
  description = "The level of logging"
  default     = "INFO"
}

variable "api_gateway_method_cache_enabled" {
  description = "Configure caching at the method level"
  default     = true
}

variable "api_gateway_method_metrics_enabled" {
  description = "Configure gathering metrics at end point level"
  default     = true
}

variable "api_gateway_tls_security_policy" {
  description = "The TLS security policy of the API Gateway when negotiating SSL handshakes"
  default     = "TLS_1_2"
}

variable "lambda_cloudwatch_logs_retention_days" {
  description = "Number of days to retain CloudWatch logs for the main search Lambda"
  type        = number
  default     = 7
}

variable "health_check_lambda_cloudwatch_logs_retention_days" {
  description = "Number of days to retain CloudWatch logs for the health check Lambda"
  type        = number
  default     = 7
}

variable "api_gateway_throttling_rate_limit" {
  description = "Throttling rate limit for the API Gateway (requests per second)"
  type        = number
}

variable "api_gateway_throttling_burst_limit" {
  description = "Throttling burst limit for the API Gateway"
  type        = number
}

# FHIR error response header mapping (Content-Type)
variable "fhir_content_type_header" {
  description = "API Gateway response header mappings for FHIR responses"
  type        = map(string)
  default = {
    "gatewayresponse.header.Content-Type" = "'application/fhir+json'"
  }
}

# Gateway response definitions for API Gateway
variable "gateway_responses" {
  description = "Map of API Gateway gateway_responses with response_type, status_code, and FHIR template"
  type = map(object({
    response_type = string
    status_code   = string
    template      = string
  }))
  # Use null default so we can compute from locals (file() not allowed in var defaults)
  default = null
}

################################################################################
# Lambda CloudWatch Alarms Configuration
################################################################################

variable "lambda_alarm_evaluation_periods" {
  description = "Number of periods over which to evaluate the alarm"
  type        = number
  default     = 2
}

variable "lambda_alarm_period" {
  description = "Period in seconds for the alarm metric evaluation"
  type        = number
  default     = 300 # 5 minutes
}

variable "search_lambda_duration_threshold_ms" {
  description = "Threshold in milliseconds for search Lambda average duration"
  type        = number
  default     = 5000 # 5 seconds
}

variable "search_lambda_concurrent_executions_threshold" {
  description = "Threshold for search Lambda concurrent executions"
  type        = number
  default     = 100
}

variable "search_lambda_errors_threshold" {
  description = "Threshold for search Lambda errors (sum over period)"
  type        = number
  default     = 5
}

variable "search_lambda_invocations_threshold" {
  description = "Minimum threshold for search Lambda invocations (alerts if below)"
  type        = number
  default     = 1
}

variable "health_check_lambda_duration_threshold_ms" {
  description = "Threshold in milliseconds for health check Lambda average duration"
  type        = number
  default     = 3000 # 3 seconds
}

variable "health_check_lambda_concurrent_executions_threshold" {
  description = "Threshold for health check Lambda concurrent executions"
  type        = number
  default     = 50
}

variable "health_check_lambda_errors_threshold" {
  description = "Threshold for health check Lambda errors (sum over period)"
  type        = number
  default     = 3
}

variable "health_check_lambda_invocations_threshold" {
  description = "Minimum threshold for health check Lambda invocations (alerts if below)"
  type        = number
  default     = 1
}

################################################################################
# Slack Notification Configuration
################################################################################

variable "slack_webhook_url_secret" {
  description = "Slack webhook URL for sending alarm notifications (stored in Secrets Manager)"
  type        = string
  sensitive   = true
  default     = "https://hooks.slack.com/services/PLACEHOLDER"
}
