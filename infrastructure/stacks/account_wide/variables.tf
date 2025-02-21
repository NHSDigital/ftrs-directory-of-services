variable "github_org" {
  description = "The name of the GitHub organization e.g. NHSDigital"
}

variable "vpc" {
  description = "A map of VPC configuration, including VPC ID, CIDR block, and other networking details"
  type        = map(any)
}

variable "enable_nat_gateway" {
  description = "Whether to create a NAT Gateway for the VPC"
  type        = bool
}

variable "single_nat_gateway" {
  description = "Whether to use a single NAT Gateway in the VPC"
  type        = bool
}

variable "create_database_subnet_group" {
  description = "Whether to create a database subnet group for RDS"
  type        = bool
}
variable "migration_pipeline_store_bucket_name" {
  description = "The name of the S3 bucket to use for the data migration pipeline"
}
