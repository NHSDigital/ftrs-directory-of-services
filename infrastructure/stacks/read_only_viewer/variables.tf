variable "commit_hash" {
  description = "The commit hash of the read-only viewer application"
  type        = string
}

variable "read_only_viewer_bucket_name" {
  description = "The name of the read-only viewer bucket"
  type        = string
}

variable "s3_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
}

variable "read_only_viewer_cloud_front_name" {
  description = "The CloudFront distribution name for read-only viewer"
  type        = string
}

variable "waf_name" {
  description = "The Web ACL name"
  type        = string
}

variable "waf_scope" {
  description = "The scope for WAF"
  type        = string
}

variable "force_destroy" {
  description = "Whether to forcefully destroy the bucket when it contains objects"
  type        = bool
  default     = true
}

variable "read_only_viewer_cloudfront_price_class" {
  description = "The price class for the CloudFront distribution"
  type        = string
  default     = "PriceClass_100"
}

variable "frontend_lambda_connection_timeout" {
  description = "The connection timeout for the frontend lambda"
  type        = number
  default     = 30
}

variable "frontend_lambda_memory_size" {
  description = "The memory size for the frontend lambda"
  type        = number
  default     = 256
}

variable "frontend_lambda_name" {
  description = "The name of the frontend lambda"
  type        = string
}

variable "frontend_lambda_runtime" {
  description = "The runtime for the frontend lambda"
  type        = string
  default     = "nodejs20.x"
}

variable "access_logs_bucket_name" {
  description = "The name of the S3 bucket for access logs"
  type        = string
  default     = "cf-access-logs"
}

variable "force_destroy_access_logging_bucket" {
  description = "Whether to forcefully destroy the bucket when it contains objects"
  type        = bool
  default     = false
}

variable "access_logs_prefix" {
  description = "The prefix for the access logs in the S3 bucket"
  type        = string
  default     = "cloudfront"
}

variable "cloudfront_5xx_error_threshold" {
  description = "Threshold percentage for CloudFront 5xx errors that triggers the alarm"
  type        = number
  default     = 5
}

variable "isShieldProactiveEngagementEnabled" {
  description = "Whether to enable Proactive Engagement for AWS Shield Advanced"
  type        = bool
}

variable "isShieldSRTAccessEnabled" {
  description = "Whether to enable Shield Response Team (SRT) access"
  type        = bool
}

variable "isShieldAutomaticResponseEnabled" {
  description = "Whether to enable Automatic Application Layer DDoS mitigation"
  type        = bool
}
