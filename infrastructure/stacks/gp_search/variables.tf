variable "gp_search_bucket_name" {
  description = "Name of S3 bucket for the GP Search API POC pipeline test"
}

variable "gp_search_lambda_name" {
  description = "Name of API Lambda for the GP Search API POC pipeline test"
}

variable "application_tag" {
  description = "The version or tag of the data mirgation application"
  type        = string
}

variable "commit_hash" {
  description = "The commit hash of the data mirgation application"
  type        = string
}
