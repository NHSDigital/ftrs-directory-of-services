variable "gp_search_bucket_name" {
  description = "Name of S3 bucket for the GP Search API POC pipeline test"
}

variable "main_project" {
  description = "The name of the main project"
}

variable "rds_name" {
  description = "The name of the main project"
}
variable "rds_instance_class" {
  description = "The instance class for the RDS instance"
  type        = string
}

variable "rds_engine" {
  description = "The engine for the RDS instance"
  type        = string
}

variable "rds_engine_version" {
  description = "The engine version for the RDS instance"
  type        = string
}

variable "rds_db_subnet_group" {
  description = "The DB RDS Subnet Group Name"
  type        = string
}
variable "rds_ingress_cidr" {
  description = "The RDS ingress CIDR blocks"
}

variable "rds_port" {
  description = "The port RDS will listen on"
  type        = string
}