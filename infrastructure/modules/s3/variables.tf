# ==============================================================================
# Mandatory variables

variable "bucket_name" { description = "The S3 bucket name" }

variable "environment" {
  description = "Deployment environment"
  type        = string
  nullable    = false

  validation {
    condition     = trimspace(var.environment) != ""
    error_message = "environment must be a non-empty string."
  }
}

# ==============================================================================
# Default variables

variable "attach_policy" { default = false }
variable "policy" { default = null }
variable "lifecycle_rule_inputs" { default = [] }

variable "target_access_logging_bucket" {
  description = "The name of the bucket where S3 to store server access logs"
  default     = null
}

variable "target_access_logging_prefix" {
  description = "A prefix for all log object keys"
  default     = null
}

variable "website_map" {
  description = "Map containing static website hosting"
  default     = {}
}

variable "force_destroy" {
  description = "Whether to forcefully destroy the bucket when it contains objects"
  type        = bool
  default     = false
}

variable "versioning" {
  description = "Whether to enable versioning on the bucket"
  type        = bool
  default     = true
}

variable "s3_logging_bucket" {
  description = "The name of the S3 bucket to use for access logs"
  type        = string
  default     = ""
}

variable "s3_encryption_key_arn" {
  description = "The ARN of the KMS key to use for server-side encryption if required"
  type        = string
  default     = null
}

variable "enable_kms_encryption" {
  description = "Whether to enable server-side KMS encryption for the S3 bucket"
  type        = bool
  default     = false
}

variable "attach_cloudtrail_log_delivery_policy" {
  description = "Whether to attach CloudTrail log delivery to the bucket policy"
  type        = bool
  default     = false
}
