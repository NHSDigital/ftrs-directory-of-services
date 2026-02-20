output "sns_topic_arn" {
  description = "ARN of the SNS topic for CloudWatch alarms"
  value       = local.stack_enabled == 1 ? aws_sns_topic.slack_notifications[0].arn : ""
}

output "lambda_function_arn" {
  description = "ARN of the Slack notification Lambda function"
  value       = local.stack_enabled == 1 ? module.slack_lambda[0].lambda_function_arn : ""
}

output "lambda_function_name" {
  description = "Name of the Slack notification Lambda function"
  value       = local.stack_enabled == 1 ? module.slack_lambda[0].lambda_function_name : ""
}

output "sns_subscription_arn" {
  description = "ARN of the SNS topic subscription"
  value       = local.stack_enabled == 1 ? aws_sns_topic_subscription.slack_notification[0].arn : ""
}
