variable "gp_search_service_name" {
  description = "The name of the gp search service"
}
variable "s3_bucket_name" {
  description = "The name of the gp search bucket"
}
variable "lambda_name" {
  description = "The name of the gp search lambda"
}
variable "health_check_lambda_name" {
  description = "The name of the health check lambda for gp search"
}
variable "lambda_runtime" {
  description = "The runtime environment for the lambda function"
}
variable "lambda_memory_size" {
  description = "The memory size of the lambda function"
  type        = number
}
variable "lambda_timeout" {
  description = "The connection timeout of the lambda function"
  type        = number
}
variable "application_tag" {
  description = "The version or tag of the gp search application"
  type        = string
  default     = "latest"
}
variable "commit_hash" {
  description = "The commit hash of the gp search application"
  type        = string
}
variable "api_gateway_access_logs_retention_days" {
  description = "The retention period in days for API Gateway logging"
  type        = number
  default     = 7
}

variable "api_gateway_payload_format_version" {
  description = "The version of the payload format"
  type        = string
  default     = "2.0"
}

variable "api_gateway_integration_timeout" {
  description = "Timeout to integration ARN"
  type        = number
}

variable "lambda_cloudwatch_logs_retention_days" {
  description = "Number of days to retain CloudWatch logs for the main search Lambda"
  type        = number
  default     = 30
}

variable "health_check_lambda_cloudwatch_logs_retention_days" {
  description = "Number of days to retain CloudWatch logs for the health check Lambda"
  type        = number
  default     = 7
}

variable "jmeter_version" {
  description = "Version of Apache JMeter to install on the EC2 instance"
  type        = string
  default     = "5.6.3"
}

variable "jmeter_instance_type" {
  description = "EC2 instance type for JMeter host"
  type        = string
  default     = "t3.small"
}

variable "jmeter_volume_size" {
  description = "Root volume size (GiB) for JMeter EC2 instance"
  type        = number
  default     = 16
}

variable "ssh_key_pair_name" {
  description = "Optional EC2 key pair name for SSH access (leave empty to disable key attachment)"
  type        = string
  default     = ""
}
