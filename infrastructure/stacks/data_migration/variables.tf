variable "migration_pipeline_store_bucket_name" {
  description = "The name of the S3 bucket to use for the data migration pipeline"
}

variable "versioning" {
  description = "Whether to enable versioning on the bucket"
  type        = bool
}
