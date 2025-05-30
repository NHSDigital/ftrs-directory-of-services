variable "application_tag" {
  description = "The version or tag of the crud api application"
  type        = string
}

variable "commit_hash" {
  description = "The commit hash of the crud api application"
  type        = string
}

variable "organisation_api_lambda_runtime" {
  description = "The runtime environment for the Lambda function"
}

variable "organisation_api_lambda_name" {
  description = "The name of the organisations api Lambda function"
}

variable "organisation_api_lambda_timeout" {
  description = "The timeout for the organisations api Lambda function"
  type        = number
}

variable "organisation_api_lambda_memory_size" {
  description = "The memory size for the organisations api Lambda function"
  type        = number
}

variable "organisation_api_lambda_handler" {
  description = "The handler for the organisations api Lambda function"
  type        = string
}

variable "crud_apis_store_bucket_name" {
  description = "The name of the S3 bucket to use for the crud apis"
}

variable "s3_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
}
