variable "alarm_name" {
  description = "Base name for the alarm"
  type        = string
}

variable "comparison_operator" {
  description = "Comparison operator for the alarm"
  type        = string
  validation {
    condition     = contains(["GreaterThanThreshold", "GreaterThanOrEqualToThreshold", "LessThanThreshold", "LessThanOrEqualToThreshold"], var.comparison_operator)
    error_message = "comparison_operator must be one of: GreaterThanThreshold, GreaterThanOrEqualToThreshold, LessThanThreshold, LessThanOrEqualToThreshold"
  }
}

variable "evaluation_periods" {
  description = "Number of periods to evaluate"
  type        = number
  validation {
    condition     = var.evaluation_periods > 0
    error_message = "evaluation_periods must be a positive integer"
  }
}

variable "metric_name" {
  description = "CloudWatch metric name"
  type        = string
}

variable "period" {
  description = "Period in seconds"
  type        = number
  validation {
    condition     = var.period > 0
    error_message = "period must be a positive integer"
  }
}

variable "statistic" {
  description = "Statistic to use (Average, Sum, Maximum, etc.) or extended statistic (p95, p99)"
  type        = string
  validation {
    condition     = contains(["SampleCount", "Average", "Sum", "Minimum", "Maximum"], var.statistic) || can(regex("^p(\\d+(\\.\\d+)?)$", var.statistic))
    error_message = "statistic must be one of: SampleCount, Average, Sum, Minimum, Maximum, or a percentile (p0-p100)"
  }
}

variable "threshold" {
  description = "Alarm threshold"
  type        = number
}

variable "alarm_description" {
  description = "Alarm description"
  type        = string
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for alarm actions"
  type        = string
}

variable "function_name" {
  description = "Lambda function name"
  type        = string
}

variable "workspace_suffix" {
  description = "Workspace suffix for naming"
  type        = string
}

variable "treat_missing_data" {
  description = "How to treat missing data (notBreaching, breaching, ignore, missing)"
  type        = string
  default     = "notBreaching"
  validation {
    condition     = contains(["notBreaching", "breaching", "ignore", "missing"], var.treat_missing_data)
    error_message = "treat_missing_data must be one of: notBreaching, breaching, ignore, missing"
  }
}

variable "actions_enabled" {
  description = "Enable or disable alarm actions (useful for placeholder alarms)"
  type        = bool
  default     = true
}

variable "namespace" {
  description = "CloudWatch namespace for the metric"
  type        = string
  default     = "AWS/Lambda"
}
