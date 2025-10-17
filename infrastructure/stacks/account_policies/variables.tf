variable "athena_output_bucket_name" {
  description = "The name of the S3 bucket for Athena query results"
  type        = string
}

variable "steampipe_role_name" {
  description = "The name of the Steampipe read-only IAM role"
  type        = string
  default     = "steampipe-readonly-role"
}
