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
}

variable "health_check_lambda_cloudwatch_logs_retention_days" {
  description = "Number of days to retain CloudWatch logs for the health check Lambda"
  type        = number
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

############################
# Global / Shared
############################
variable "lambda_alarm_evaluation_periods" {
  description = "Default number of periods over which to evaluate alarms (unless overridden per metric/severity)"
  type        = number
  default     = 2
}

variable "lambda_alarm_period_seconds" {
  description = "Default CloudWatch period in seconds for alarm metric evaluation (Lambda metrics are 60s by default)"
  type        = number
  default     = 60
}

############################
# SEARCH LAMBDA
# Duration (Execution Time)
# CRITICAL: p99 > 800 ms (active)
# WARNING: p95 placeholder (disabled until baseline established)
############################
variable "search_lambda_duration_p95_warning_ms" {
  description = "Search Lambda duration p95 warning threshold in milliseconds (placeholder - disabled)"
  type        = number
  default     = 600
}

variable "search_lambda_duration_p99_critical_ms" {
  description = "Search Lambda duration p99 critical threshold in milliseconds"
  type        = number
  default     = 800
}

############################
# SEARCH LAMBDA
# Concurrency (In-Flight Load)
# CRITICAL: >= 100 (active)
# WARNING: placeholder (disabled until baseline established)
############################
variable "search_lambda_concurrent_executions_warning" {
  description = "Search Lambda concurrency warning threshold (placeholder - disabled)"
  type        = number
  default     = 80
}

variable "search_lambda_concurrent_executions_critical" {
  description = "Search Lambda concurrency critical threshold (ConcurrentExecutions)"
  type        = number
  default     = 100
}

############################
# SEARCH LAMBDA
# Throttles (Capacity Rejections)
# CRITICAL: > 0 for 1 minute (active)
############################
# Critical (strict) — use period=60s, evaluation_periods=1
variable "lambda_throttles_critical_period_seconds" {
  description = "CloudWatch period in seconds for throttles CRITICAL alarm"
  type        = number
  default     = 60
}

variable "lambda_throttles_critical_evaluation_periods" {
  description = "Evaluation periods for throttles CRITICAL alarm"
  type        = number
  default     = 1
}

variable "search_lambda_throttles_critical_threshold" {
  description = "Search Lambda throttles CRITICAL threshold (set to 0, alarm if > 0)"
  type        = number
  default     = 0
}

############################
# SEARCH LAMBDA
# Invocations (Workload Volume)
# CRITICAL: spike > 2x baseline (active)
############################
variable "search_lambda_invocations_baseline_per_hour" {
  description = "Baseline invocations per hour for Search Lambda"
  type        = number
  default     = 300
}

variable "invocations_critical_spike_multiplier" {
  description = "Multiplier over baseline to trigger CRITICAL spike alarm (e.g., 2 => >2x baseline)"
  type        = number
  default     = 2
}

############################
# SEARCH LAMBDA
# Errors
# CRITICAL: > 1 (active)
# WARNING: placeholder (disabled until baseline established)
############################
variable "search_lambda_errors_warning_threshold" {
  description = "Search Lambda errors WARNING threshold (placeholder - disabled)"
  type        = number
  default     = 5
}

variable "search_lambda_errors_critical_threshold" {
  description = "Search Lambda errors CRITICAL threshold (sum over period)"
  type        = number
  default     = 1
}

############################
# HEALTH CHECK LAMBDA (/_status)
# Only one metric needed per OBS-003:
# Errors for health_check_function
# Critical: > 0 for 1 minute
# Warning: N/A (no warning)
############################
variable "health_check_errors_critical_threshold" {
  description = "Health Check Lambda errors CRITICAL threshold (set to 0, alarm if > 0)"
  type        = number
  default     = 0
}

variable "health_check_errors_critical_period_seconds" {
  description = "CloudWatch period in seconds for Health Check errors CRITICAL alarm"
  type        = number
  default     = 60
}

variable "health_check_errors_critical_evaluation_periods" {
  description = "Evaluation periods for Health Check errors CRITICAL alarm"
  type        = number
  default     = 1
}

################################################################################
# Alarm Actions Control
################################################################################

variable "enable_warning_alarms" {
  description = "Enable actions for WARNING severity alarms (set to false to create placeholders)"
  type        = bool
  default     = false
}

################################################################################
# Slack Notification Configuration
################################################################################

variable "slack_webhook_alarms_url" {
  description = "Slack webhook URL for sending alarm notifications"
  type        = string
  sensitive   = true
  default     = ""

  validation {
    condition     = var.slack_webhook_alarms_url == "" || can(regex("^https://hooks\\.slack\\.com/", var.slack_webhook_alarms_url))
    error_message = "The slack_webhook_alarms_url must be a valid Slack webhook URL starting with https://hooks.slack.com/ or empty string."
  }
}
