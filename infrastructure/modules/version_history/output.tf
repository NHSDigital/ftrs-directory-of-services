output "lambda_function_arn" {
  description = "The ARN of the version history Lambda function"
  value       = module.version_history_lambda.lambda_function_arn
}

output "lambda_function_name" {
  description = "The name of the version history Lambda function"
  value       = module.version_history_lambda.lambda_function_name
}
