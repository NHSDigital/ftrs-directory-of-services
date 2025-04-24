variable "application_tag" {
  description = "The version or tag of the data mirgation application"
  type        = string
}

variable "commit_hash" {
  description = "The commit hash of the data mirgation application"
  type        = string
}

variable "lambda_runtime" {
  description = "The runtime environment for the Lambda function"
}

variable "aws_lambda_layers" {
  description = "A list of Lambda layer ARNs to attach to the Lambda function"
  type        = list(string)
}

variable "extract_name" {
  description = "The extract name of the Lambda function"
}

variable "extract_lambda_connection_timeout" {
  description = "The timeout for the extract Lambda function"
  type        = number
}

variable "extract_lambda_memory_size" {
  description = "The memory size for the extract Lambda function"
  type        = number
}

variable "extract_lambda_handler" {
  description = "The handler for the extract Lambda function"
  type        = string
}

variable "transform_name" {
  description = "The transform name of the Lambda function"
}

variable "transform_lambda_connection_timeout" {
  description = "The timeout for the transform Lambda function"
  type        = number
}

variable "transform_lambda_memory_size" {
  description = "The memory size for the transform Lambda function"
  type        = number
}

variable "transform_lambda_handler" {
  description = "The handler for the transform Lambda function"
  type        = string
}

variable "data_collection_date" {
  description = "The date the data has been collected"
  type        = string
}

variable "load_name" {
  description = "The load name of the Lambda function"
}

variable "load_lambda_connection_timeout" {
  description = "The timeout for the load Lambda function"
  type        = number
}

variable "load_lambda_memory_size" {
  description = "The memory size for the load Lambda function"
  type        = number
}

variable "load_lambda_handler" {
  description = "The handler for the load Lambda function"
  type        = string
}
