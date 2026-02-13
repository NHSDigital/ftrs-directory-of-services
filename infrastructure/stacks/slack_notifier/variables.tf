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
