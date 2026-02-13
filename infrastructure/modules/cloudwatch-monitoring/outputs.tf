output "sns_topic_arn" {
  description = "ARN of the SNS topic for alarm notifications"
  value       = module.sns.topic_arn
}

output "sns_topic_name" {
  description = "Name of the SNS topic"
  value       = module.sns.topic_name
}

output "alarm_arns" {
  description = "Map of alarm names to their ARNs"
  value       = { for k, v in module.cloudwatch_alarms : k => v.alarm_arn }
}
