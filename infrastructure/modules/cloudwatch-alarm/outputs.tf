output "alarm_arn" {
  description = "ARN of the CloudWatch alarm"
  value       = module.metric_alarm.cloudwatch_metric_alarm_arn
}

output "alarm_name" {
  description = "Name of the CloudWatch alarm"
  value       = module.metric_alarm.cloudwatch_metric_alarm_id
}

output "alarm_id" {
  description = "ID of the CloudWatch alarm"
  value       = module.metric_alarm.cloudwatch_metric_alarm_id
}
