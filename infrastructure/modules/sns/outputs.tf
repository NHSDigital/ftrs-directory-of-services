output "topic_arn" {
  description = "ARN of the SNS topic"
  value       = module.sns_topic.topic_arn
}

output "topic_name" {
  description = "Name of the SNS topic"
  value       = module.sns_topic.topic_name
}
