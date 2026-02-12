variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project" {
  description = "Project name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "sns_topic_arn" {
  description = "ARN of the SNS topic to subscribe to"
  type        = string
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alarm notifications"
  type        = string
  sensitive   = true

  validation {
    condition     = var.slack_webhook_url == "" || can(regex("^https://hooks\\.slack\\.com/", var.slack_webhook_url))
    error_message = "The slack_webhook_url must be a valid Slack webhook URL starting with https://hooks.slack.com/ or empty string."
  }
}

variable "lambda_module_source" {
  description = "Source path for the Lambda module"
  type        = string
  default     = "github.com/NHSDigital/ftrs-directory-of-services//infrastructure/modules/lambda"
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Lambda memory size in MB"
  type        = number
  default     = 128
}

variable "lambda_layers" {
  description = "List of Lambda layer ARNs"
  type        = list(string)
  default     = []
}

variable "security_group_ids" {
  description = "List of security group IDs for Lambda"
  type        = list(string)
}

variable "cloudwatch_logs_retention_days" {
  description = "CloudWatch Logs retention period in days"
  type        = number
  default     = 7
}

variable "enable_xray_tracing" {
  description = "Enable AWS X-Ray tracing"
  type        = bool
  default     = true
}

variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
}

variable "artefacts_bucket_name" {
  description = "Name of the S3 bucket containing Lambda artifacts"
  type        = string
}

variable "lambda_artifact_key" {
  description = "S3 key for Lambda deployment package"
  type        = string
}
