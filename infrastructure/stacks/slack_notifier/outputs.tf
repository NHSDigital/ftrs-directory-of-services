output "sns_topic_arn" {
  description = "ARN of the SNS topic for CloudWatch alarms"
  value       = aws_sns_topic.slack_notifications.arn
}

output "lambda_function_arn" {
  description = "ARN of the Slack notification Lambda function"
  value       = module.slack_notifications.lambda_function_arn
}

output "lambda_function_name" {
  description = "Name of the Slack notification Lambda function"
  value       = module.slack_notifications.lambda_function_name
}

output "sns_subscription_arn" {
  description = "ARN of the SNS topic subscription"
  value       = module.slack_notifications.sns_subscription_arn
}
