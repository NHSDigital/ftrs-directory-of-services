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

variable "vpc" {
  description = "The VPN IP address range"
  type        = map(string)
}
