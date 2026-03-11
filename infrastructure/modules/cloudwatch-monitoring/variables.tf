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

variable "resource_additional_dimensions" {
  description = "Map of resource keys to additional dimensions that override or supplement those from the alarm config (e.g., to replace placeholder values)"
  type        = map(map(string))
  default     = {}
}

variable "slack_notifier_function_name" {
  description = "Name of the Slack notifier Lambda function"
  type        = string
}
