variable "s3_logging_expiration_days" {
  description = "The number of days before the S3 access logs are deleted"
  type        = number
  default     = 30
}

variable "s3_logging_bucket_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
}
