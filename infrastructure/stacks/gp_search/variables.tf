variable "gp_search_service_name" {
  description = "The name of the gp search service"
}
variable "s3_bucket_name" {
  description = "The name of the gp search bucket"
}
variable "lambda_name" {
  description = "The name of the gp search lambda"
}
variable "application_tag" {
  description = "The version or tag of the gp search application"
  type        = string
}
variable "commit_hash" {
  description = "The commit hash of the gp search application"
  type        = string
}
