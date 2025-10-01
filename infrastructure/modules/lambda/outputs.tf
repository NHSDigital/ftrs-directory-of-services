output "lambda_name" {
  value = module.lambda.lambda_function_name
}

output "lambda_arn" {
  value = module.lambda.lambda_function_arn
}

output "lambda_function_arn" {
  value = module.lambda.lambda_function_arn
}

output "lambda_function_invoke_arn" {
  description = "The Invoke ARN of the Lambda Function"
  value       = module.lambda.lambda_function_invoke_arn
}

output "lambda_function_name" {
  value = module.lambda.lambda_function_name
}

output "lambda_role_arn" {
  value = module.lambda.lambda_role_arn
}

output "lambda_cloudwatch_log_group_name" {
  value = module.lambda.lambda_cloudwatch_log_group_name
}
