output "topic_arn" {
  description = "ARN of the SNS topic"
  value       = aws_sns_topic.dos_search_lambda_alarms.arn
}

output "topic_name" {
  description = "Name of the SNS topic"
  value       = aws_sns_topic.dos_search_lambda_alarms.name
}
