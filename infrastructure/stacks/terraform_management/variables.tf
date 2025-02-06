variable "terraform_lock_table_name" {
  description = "Name of dynamodb table that holds terraformn state locks"
}

variable "terraform_state_bucket_name" {
  description = "Name of s3 bucket that holds terraform state"
}

variable "s3_versioning" {
  description = "Whether versioning is enabled for the S3 bucket that holds the Terraform state"
  type        = bool
}
