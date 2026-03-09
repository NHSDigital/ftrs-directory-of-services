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

variable "slack_notifier_enabled" {
  description = "Enable Slack notifier subscription to SNS topic"
  type        = bool
  default     = false
}

variable "slack_notifier_function_name" {
  description = "Name of the Slack notifier Lambda function"
  type        = string
  default     = ""
}

variable "alarm_descriptions" {
  description = "Map of resource keys to their alarm descriptions"
  type        = map(map(string))
  default     = {}
}

variable "alarm_datapoints_to_alarm" {
  description = "Map of resource keys to their datapoints to alarm configuration"
  type        = map(map(number))
  default     = {}
}