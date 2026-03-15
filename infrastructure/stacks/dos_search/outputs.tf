output "sns_topic_arn" {
  description = "ARN of the SNS topic for alarms"
  value = coalesce(
    module.api_gateway_monitoring.sns_topic_arn,
    local.is_primary_environment ? module.lambda_monitoring[0].sns_topic_arn : null
  )
}

output "sns_topic_name" {
  description = "Name of the SNS topic for alarms"
  value = coalesce(
    module.api_gateway_monitoring.sns_topic_name,
    local.is_primary_environment ? module.lambda_monitoring[0].sns_topic_name : null
  )
}

output "alarm_arns" {
  description = "Map of all alarm names to their ARNs"
  value = merge(
    module.api_gateway_monitoring.alarm_arns,
    local.is_primary_environment ? module.lambda_monitoring[0].alarm_arns : {}
  )
}
