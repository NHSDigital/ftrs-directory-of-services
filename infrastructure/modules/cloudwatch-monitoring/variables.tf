variable "resource_prefix" {
  description = "Prefix for alarm names"
  type        = string
}

variable "workspace_suffix" {
  description = "Workspace suffix for resource naming"
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
  default     = null
}

variable "tags" {
  description = "Tags to apply to SNS topic"
  type        = map(string)
  default     = {}
}

variable "alarm_config_path" {
  description = "Path to JSON file containing alarm configurations. Use module templates or provide custom path"
  type        = string
  default     = "standard"
}

variable "monitored_resources" {
  description = "Map of resource keys to their identifiers (e.g., Lambda function names, API Gateway IDs, WAF WebACL names)"
  type        = map(string)
  default     = {}
}

variable "lambda_functions" {
  description = "(Deprecated: use monitored_resources) Map of lambda function keys to their names"
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
