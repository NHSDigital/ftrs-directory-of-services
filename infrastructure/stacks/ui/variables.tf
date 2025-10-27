variable "application_tag" {
  description = "The version or tag of the etl_ode_code application"
  type        = string
}

variable "commit_hash" {
  description = "The commit hash of the UI"
  type        = string
}

variable "ui_bucket_name" {
  description = "The name of the UI bucket"
  type        = string
}

variable "s3_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
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

variable "ui_cloudfront_price_class" {
  description = "The price class for the CloudFront distribution"
  type        = string
  default     = "PriceClass_100"
}

variable "ui_lambda_connection_timeout" {
  description = "The connection timeout for the frontend lambda"
  type        = number
  default     = 30
}

variable "ui_lambda_memory_size" {
  description = "The memory size for the frontend lambda"
  type        = number
  default     = 256
}

variable "ui_lambda_name" {
  description = "The name of the frontend lambda"
  type        = string
}

variable "ui_lambda_runtime" {
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
  default     = 2
}

variable "cloudfront_4xx_error_threshold" {
  description = "Threshold percentage for CloudFront 4xx errors that triggers the alarm"
  type        = number
  default     = 5
}

variable "cloudfront_latency_threshold" {
  description = "Threshold in milliseconds for CloudFront latency that triggers the alarm"
  type        = number
  default     = 2000
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

variable "realtime_metrics_subscription_status" {
  description = "The status of additional CloudWatch Metrics for CloudFront distributions"
  type        = string
}

variable "alarm_notification_email" {
  description = "List of email addresses to receive SNS notifications for Shield DDoS alarms"
  type        = list(string)
}

variable "emergency_contacts" {
  description = "List of emergency contacts for Proactive engagement from AWS Shield Advanced SRT"
  type = list(object({
    email_address = string
    phone_number  = string
    contact_notes = optional(string)
  }))
}

variable "create_monitoring_subscription" {
  description = "The resource for monitoring subscription will be created."
  type        = bool
}

variable "http_version" {
  description = "The HTTP version for CloudFront distribution"
  type        = string
  default     = "http2and3"

}

variable "origin_protocol_policy" {
  description = "The origin protocol policy for CloudFront distribution"
  type        = string
  default     = "https-only"

}

variable "origin_ssl_protocols" {
  description = "The origin SSL protocols for CloudFront distribution"
  type        = list(string)
  default     = ["TLSv1.2"]
}

variable "ssl_support_method" {
  description = "The SSL support method for CloudFront distribution"
  type        = string
  default     = "sni-only"
}

variable "minimum_protocol_version" {
  description = "The minimum protocol version for CloudFront distribution"
  type        = string
  default     = "TLSv1.2_2021"
}
