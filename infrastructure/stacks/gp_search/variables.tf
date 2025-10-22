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
  default     = 30
  validation {
    condition     = var.jmeter_volume_size >= 30
    error_message = "jmeter_volume_size must be >= 30 GiB to satisfy the AMI snapshot minimum size"
  }
}

variable "attach_s3_read" {
  description = "If true, attach an inline policy to allow s3:GetObject/ListBucket on specified buckets"
  type        = bool
  default     = false
}

variable "s3_read_bucket_arns" {
  description = "List of S3 bucket ARNs to grant read access to (when attach_s3_read is true)"
  type        = list(string)
  default     = []
}

variable "kms_key_arns" {
  description = "Optional list of KMS key ARNs to allow kms:Decrypt (for reading KMS-encrypted S3 objects or parameters)"
  type        = list(string)
  default     = []
}

variable "jmeter_poweroff_after_setup" {
  description = "If true (default), power off the JMeter instance at the end of user-data setup"
  type        = bool
  default     = true
}

variable "jmeter_ami_name_pattern" {
  description = "Name pattern(s) used to filter AMIs when discovering the latest AMI (default matches Amazon Linux 2023 x86_64). Example: [\"al2023-ami-*-x86_64\"]"
  type        = list(string)
  default     = ["al2023-ami-*-x86_64"]
}

variable "jmeter_ami_architectures" {
  description = "List of AMI architectures to filter by (e.g. [\"x86_64\"] or [\"aarch64\"]). Default is [\"x86_64\"]."
  type        = list(string)
  default     = ["x86_64"]
}

