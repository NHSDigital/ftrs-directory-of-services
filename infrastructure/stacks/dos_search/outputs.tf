output "lambda_monitoring_sns_topic_arn" {
  description = "ARN of the Lambda monitoring SNS topic"
  value       = module.lambda_monitoring.sns_topic_arn
}

output "lambda_monitoring_sns_topic_name" {
  description = "Name of the Lambda monitoring SNS topic"
  value       = module.lambda_monitoring.sns_topic_name
}
