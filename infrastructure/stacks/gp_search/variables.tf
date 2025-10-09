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

#####################################################

# API Gateway

variable "api_gateway_name" {
  description = "The name of the API Gateway"
  default     = "default"
}

variable "api_gateway_description" {
  description = "The description of the API Gateway"
  default     = "DoS Search API"
}

variable "api_gateway_log_group_class" {
  description = "The logging group class of the API Gateway log group"
  default     = "STANDARD"
}

variable "api_gateway_log_group_retention_days" {
  description = "The period of time in days to retain logs for the API Gateway log group"
  default     = "7"
}

variable "api_gateway_xray_tracing" {
  description = "Flag to enable or disable xray tracing at the API Gateway"
  default     = true
}

variable "api_gateway_cache_cluster_enabled" {
  description = "Flag to enable or disable caching at the API Gateway"
  default     = true
}

variable "api_gateway_cache_cluster_size" {
  description = "If caching at the API Gateway is enabled, the size of the cache"
  default     = 0.5
}

variable "api_gateway_logging_level" {
  description = "The level of logging"
  default     = "INFO"
}

variable "api_gateway_method_cache_enabled" {
  description = "Configure caching at the method level"
  default     = true
}

variable "api_gateway_method_metrics_enabled" {
  description = "Configure gathering metrics at end point level"
  default     = true
}

variable "api_gateway_tls_security_policy" {
  description = "The TLS security policy of the API Gateway when negotiating SSL handshakes"
  default     = "TLS_1_2"
}
