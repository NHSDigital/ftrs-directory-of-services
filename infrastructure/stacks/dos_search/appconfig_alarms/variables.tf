variable "sns_topic_arn" {
  description = "ARN of the SNS topic for alarm notifications"
  type        = string
}

variable "search_lambda_function_name" {
  description = "Name of the search Lambda function"
  type        = string
}

variable "health_check_lambda_function_name" {
  description = "Name of the health check Lambda function"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}
