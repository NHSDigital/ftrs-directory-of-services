# ==============================================================================
# Mandatory variables

variable "bucket_name" { description = "The S3 bucket name" }

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
