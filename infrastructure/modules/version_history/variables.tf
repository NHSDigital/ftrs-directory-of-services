variable "resource_prefix" {
  description = "The resource prefix for naming"
  type        = string
}

variable "lambda_name" {
  description = "The name of the version history Lambda function"
  type        = string
}

variable "lambda_handler" {
  description = "The handler for the version history Lambda function"
  type        = string
}

variable "lambda_runtime" {
  description = "The runtime for the Lambda function"
  type        = string
}

variable "lambda_timeout" {
  description = "The timeout for the version history Lambda function"
  type        = number
}

variable "lambda_memory_size" {
  description = "The memory size for the version history Lambda function"
  type        = number
}

variable "lambda_logs_retention" {
  description = "The logs retention for the version history Lambda function"
  type        = number
}

variable "batch_size" {
  description = "The batch size for DynamoDB stream event source mappings"
  type        = number
}

variable "maximum_concurrency" {
  description = "The maximum concurrency for DynamoDB stream event source mappings"
  type        = number
}

variable "artefacts_bucket" {
  description = "The S3 bucket containing Lambda artifacts"
  type        = string
}

variable "lambda_s3_key" {
  description = "The S3 key for the Lambda deployment package"
  type        = string
}

variable "lambda_s3_key_version_id" {
  description = "The S3 version ID for the Lambda deployment package"
  type        = string
}

variable "lambda_layers" {
  description = "List of Lambda layer ARNs"
  type        = list(string)
}

variable "subnet_ids" {
  description = "List of subnet IDs for the Lambda function"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs for the Lambda function"
  type        = list(string)
}

variable "version_history_table_name" {
  description = "The name of the version history DynamoDB table"
  type        = string
}

variable "version_history_table_arn" {
  description = "The ARN of the version history DynamoDB table"
  type        = string
}

variable "organisation_stream_arn" {
  description = "The DynamoDB stream ARN for the organisation table"
  type        = string
}

variable "location_stream_arn" {
  description = "The DynamoDB stream ARN for the location table"
  type        = string
}

variable "healthcare_service_stream_arn" {
  description = "The DynamoDB stream ARN for the healthcare-service table"
  type        = string
}

variable "organisation_table_arn" {
  description = "The ARN of the organisation table"
  type        = string
}

variable "location_table_arn" {
  description = "The ARN of the location table"
  type        = string
}

variable "healthcare_service_table_arn" {
  description = "The ARN of the healthcare-service table"
  type        = string
}

variable "environment" {
  description = "The environment name"
  type        = string
}

variable "workspace" {
  description = "The terraform workspace"
  type        = string
}

variable "project" {
  description = "The project name"
  type        = string
}

variable "account_id" {
  description = "The AWS account ID"
  type        = string
}

variable "account_prefix" {
  description = "The account prefix"
  type        = string
}

variable "aws_region" {
  description = "The AWS region"
  type        = string
}

variable "vpc_id" {
  description = "The VPC ID"
  type        = string
}
