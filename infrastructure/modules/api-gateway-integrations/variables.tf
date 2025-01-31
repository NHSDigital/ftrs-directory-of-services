# ==============================================================================
# Mandatory variables
variable "aws_region" {
  description = "AWS region identifier"
}
variable "lambda_function_name" {
  description = "Name of lambda function"
}

variable "http_method" {
  description = "Http method for integration - GET POST etc"
}

variable "rest_api_id" {
  description = "Id of rest api"
}

variable "gateway_resource_id" {
  description = "Id of api gateway resource"
}
variable "account_id" {
  description = "Id of AWS account"
}

# ==============================================================================
# Default variables


