variable "data_migration_stack" {
  description = "The name of the data migration stack"
}
variable "gp_search_service_name" {
  description = "The name of the gp search service"
}
variable "s3_bucket_name" {
  description = "The name of the gp search bucket"
}
variable "lambda_name" {
  description = "The name of the gp search lambda"
}
variable "lambda_runtime" {
  description = "The runtime environment for the lambda function"
}
variable "lambda_memory_size" {
  description = "The memory size of the lambda function"
  type        = number
}
variable "lambda_timeout" {
  description = "The connection timeout of the lambda function"
  type        = number
}
variable "aws_lambda_layers" {
  description = "A list of Lambda layer ARNs to attach to the lambda function"
  type        = list(string)
}
variable "db_secret_name" {
  description = "The name of the secret store for database secrets"
}
variable "rds_port" {
  description = "The port RDS will listen on"
  type        = string
}
variable "application_tag" {
  description = "The version or tag of the gp search application"
  type        = string
}
variable "commit_hash" {
  description = "The commit hash of the gp search application"
  type        = string
}
