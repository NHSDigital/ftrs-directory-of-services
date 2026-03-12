output "sns_topic_arn" {
  description = "ARN of the SNS topic for alarm notifications"
  value       = var.external_sns_topic_arn != null ? var.external_sns_topic_arn : aws_sns_topic.alarms[0].arn
}

output "sns_topic_name" {
  description = "Name of the SNS topic"
  value       = var.external_sns_topic_arn != null ? null : aws_sns_topic.alarms[0].name
}

output "alarm_arns" {
  description = "Map of alarm names to their ARNs"
  value       = { for k, v in module.metric_alarm : k => v.cloudwatch_metric_alarm_arn }
}
