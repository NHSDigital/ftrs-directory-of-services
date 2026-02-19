variable "slack_webhook_alarms_url" {
  description = "Slack webhook URL for alarm notifications"
  type        = string
  sensitive   = true

  validation {
    condition     = var.slack_webhook_alarms_url == "" || can(regex("^https://hooks\\.slack\\.com/", var.slack_webhook_alarms_url))
    error_message = "The slack_webhook_alarms_url must be a valid Slack webhook URL starting with https://hooks.slack.com/ or empty string."
  }
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 128
}

variable "cloudwatch_logs_retention_days" {
  description = "CloudWatch logs retention in days"
  type        = number
  default     = 7
}

variable "enable_xray_tracing" {
  description = "Enable X-Ray tracing for Lambda function"
  type        = bool
  default     = true
}

variable "allow_slack_webhook_egress" {
  description = "Allows HTTPS egress to the internet for Slack webhooks"
  type        = string
  default     = "0.0.0.0/0"
}
