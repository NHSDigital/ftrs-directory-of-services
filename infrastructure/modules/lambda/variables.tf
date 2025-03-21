# ==============================================================================
# Mandatory variables

variable "function_name" {
  description = "The function name of the Lambda"
}

variable "description" {
  description = "The description of the Lambda"
}

variable "policy_jsons" {
  description = "List of JSON policies for Lambda"
}

# ==============================================================================
# Default variables

variable "handler" {
  description = "Handler function entry point"
  default     = "app.lambda_handler"
}

variable "runtime" {
  description = "Runtime environment for the Lambda function"
  default     = "python3.12"
}

variable "publish" {
  description = "Whether to publish a new Lambda version on update"
  default     = true
}

variable "create_package" {
  description = "Whether to create a new ZIP package or use an existing one"
  default     = false
}

variable "local_existing_package" {
  description = "Path to the local ZIP file if using a pre-existing package"
  default     = "./misc/init.zip"
}

variable "ignore_source_code_hash" {
  description = "Whether to ignore changes to the source code hash"
  default     = true
}

variable "attach_policy_jsons" {
  description = "Whether to attach the provided JSON policies to the Lambda role"
  default     = true
}

variable "number_of_policy_jsons" {
  description = "Number of JSON policies to attach"
  default     = "1"
}

variable "environment_variables" {
  description = "Map of environment variables"
  default     = {}
}

variable "layers" {
  description = "The name of the Lambda layers"
  default     = []
}

variable "memory_size" {
  description = "Amount of memory in MB your Lambda Function can use at runtime"
  default     = "128"
}

variable "timeout" {
  description = "Timeout of the lambda function in seconds"
  default     = "3"
}

variable "log_retention" {
  description = "Length of time to keep the logs in cloudwatch"
  default     = "0"
}

variable "subnet_ids" {
  description = "List of subnet IDs for the Lambda function VPC configuration"
}

variable "security_group_ids" {
  description = "List of security group IDs for the Lambda function VPC configuration"
}
