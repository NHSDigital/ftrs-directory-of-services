variable "alarm_name" {
  description = "Base name for the alarm"
  type        = string
}

variable "comparison_operator" {
  description = "Comparison operator for the alarm"
  type        = string
}

variable "evaluation_periods" {
  description = "Number of periods to evaluate"
  type        = number
}

variable "metric_name" {
  description = "CloudWatch metric name"
  type        = string
}

variable "period" {
  description = "Period in seconds"
  type        = number
}

variable "statistic" {
  description = "Statistic to use (Average, Sum, Maximum, etc.)"
  type        = string
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

resource "aws_cloudwatch_metric_alarm" "alarm" {
  alarm_name          = "${var.alarm_name}${var.workspace_suffix}"
  comparison_operator = var.comparison_operator
  evaluation_periods  = var.evaluation_periods
  metric_name         = var.metric_name
  namespace           = "AWS/Lambda"
  period              = var.period
  statistic           = var.statistic
  threshold           = var.threshold
  alarm_description   = var.alarm_description
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = var.function_name
  }

  tags = {
    Name = "${var.alarm_name}${var.workspace_suffix}"
  }
}
