variable "resource_prefix" {
  description = "Prefix for alarm names"
  type        = string
}

variable "sns_topic_name" {
  description = "Name of the SNS topic for alarm notifications"
  type        = string
}

variable "sns_display_name" {
  description = "Display name for the SNS topic"
  type        = string
}

variable "kms_key_id" {
  description = "KMS key ID for SNS topic encryption"
  type        = string
}

variable "tags" {
  description = "Tags to apply to SNS topic"
  type        = map(string)
  default     = {}
}

variable "alarm_config_path" {
  description = "Template name for alarm configurations (e.g., 'lambda/config', 'api-gateway/config', 'waf/config')"
  type        = string
}

variable "monitored_resources" {
  description = "Map of resource keys to their identifiers (e.g., Lambda function names, API Gateway names, WAF WebACL names)"
  type        = map(string)
  default     = {}
}

variable "alarm_thresholds" {
  description = "Map of resource keys to their alarm thresholds"
  type        = map(map(number))
}

variable "alarm_evaluation_periods" {
  description = "Map of resource keys to their evaluation periods"
  type        = map(map(number))
}

variable "alarm_periods" {
  description = "Map of resource keys to their period in seconds"
  type        = map(map(number))
}

variable "enable_warning_alarms" {
  description = "Enable or disable warning level alarms"
  type        = bool
  default     = true
}

variable "resource_metadata" {
  description = "Map of resource keys to their metadata (api_path, service)"
  type = map(object({
    api_path = string
    service  = string
  }))
  default = {}
}

variable "resource_extra_dimensions" {
  description = "Map of resource keys to alarm suffixes to extra CloudWatch dimensions (e.g. for AWS/WAFV2 Region)"
  type        = map(map(map(string)))
  default     = {}
}

variable "slack_notifier_function_name" {
  description = "Name of the Slack notifier Lambda function"
  type        = string
}

variable "api_gateway_log_group_name" {
  description = "CloudWatch log group name for API Gateway access logs (required for 429 metric filter)"
  type        = string
  default     = null
}

variable "rate_limiting_429_critical_threshold" {
  description = "Critical threshold for 429 rate limiting alarm (null disables it)"
  type        = number
  default     = null
}

variable "rate_limiting_429_critical_period" {
  description = "Period in seconds for 429 critical alarm"
  type        = number
  default     = 60
}

variable "rate_limiting_429_critical_evaluation_periods" {
  description = "Evaluation periods for 429 critical alarm"
  type        = number
  default     = 1
}

variable "rate_limiting_429_warning_threshold" {
  description = "Warning threshold for 429 rate limiting alarm (null disables it)"
  type        = number
  default     = null
}

variable "rate_limiting_429_warning_period" {
  description = "Period in seconds for 429 warning alarm"
  type        = number
  default     = 300
}

variable "rate_limiting_429_warning_evaluation_periods" {
  description = "Evaluation periods for 429 warning alarm"
  type        = number
  default     = 1
}

variable "rate_limiting_429_metric_namespace" {
  description = "CloudWatch custom metric namespace for 429 rate limiting"
  type        = string
  default     = "Custom/ApiGateway"
}

variable "rate_limiting_429_metric_name" {
  description = "CloudWatch custom metric name for 429 rate limiting"
  type        = string
  default     = "429RateLimitedRequests"
}
