output "lambda_monitoring_sns_topic_arn" {
  description = "ARN of the Lambda monitoring SNS topic"
  value       = try(module.lambda_monitoring[0].sns_topic_arn, null)
}

output "lambda_monitoring_sns_topic_name" {
  description = "Name of the Lambda monitoring SNS topic"
  value       = try(module.lambda_monitoring[0].sns_topic_name, null)
}
