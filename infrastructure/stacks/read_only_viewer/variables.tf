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

variable "read_only_viewer_waf_name" {
  description = "The Web ACL name for read-only viewer"
  type        = string
}

variable "read_only_viewer_ip_set_name" {
  description = "The IP set name for read only viewer"
  type        = string
}

variable "read_only_viewer_waf_scope" {
  description = "The scope for WAF"
  type        = string
}

variable "force_destroy" {
  description = "Whether to forcefully destroy the bucket when it contains objects"
  type        = bool
  default     = true
}

variable "read_only_viewer_log_group" {
  description = "Name for the WAF Web ACL log group"
  type        = string
}

variable "read_only_viewer_log_group_retention_days" {
  description = "The retention period for the Read only viewer Web ACL Log group"
  type        = number
  default     = 365
}

variable "read_only_viewer_log_group_class" {
  description = "The log group class to use"
  type        = string
}

variable "read_only_viewer_waf_web_acl_log_group_policy_name" {
  description = "The log group policy name"
  type        = string
}

variable "read_only_viewer_log_group_name_prefix" {
  description = "Prefix for WAF CloudWatch Log Group Name"
  type        = string
  default     = "aws-waf-logs-"
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
