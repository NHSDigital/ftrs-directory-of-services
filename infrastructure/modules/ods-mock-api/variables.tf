variable "api_gateway_name" {
  description = "The name of the ODS Mock API Gateway (mock service for testing)"
  type        = string
}

variable "api_gateway_description" {
  description = "The description of the ODS Mock API Gateway (simulates real ODS API for development/testing)"
  type        = string
}

# API Gateway rate limiting settings

variable "throttle_burst_limit" {
  description = "Mock API Gateway throttle burst limit"
  type        = number
  default     = 100
}

variable "throttle_rate_limit" {
  description = "Mock API Gateway throttle rate limit"
  type        = number
  default     = 50
}

variable "quota_limit" {
  description = "Mock API key quota limit per day"
  type        = number
  default     = 1000
}
