variable "main_project" {
  description = "The name of the main project"
}

variable "rds_name" {
  description = "The name of the main project"
}

variable "engine" {
  description = "The engine for the RDS instance"
  type        = string
}

variable "engine_version" {
  description = "The engine version for the RDS instance"
  type        = string
}

variable "rds_instance_class" {
  description = "The instance class for the RDS instance"
  type        = string
}

variable "rds_db_subnet_group" {
  description = "The DB RDS Subnet Group Name"
  type        = string
}

variable "rds_ingress_cidr" {
  description = "The RDS ingress CIDR blocks"
}

# variable "migration_pipeline_store_bucket_name" {
#   description = "The name of the S3 bucket to use for the data migration pipeline"
# }

# variable "s3_versioning" {
#   description = "Whether to enable versioning on the S3 bucket"
#   type        = bool
# }

# variable "rds_database" {
#   description = "The name of the RDS database"
#   type        = string
# }

variable "rds_port" {
  description = "The port RDS will listen on"
  type        = string
}

# variable "rds_engine_mode" {
#   description = "The engine mode for the RDS instance"
#   type        = string
# }


# variable "data_migration_rds_min_capacity" {
#   description = "The minimum capacity for the RDS instance"
#   type        = number
# }

# variable "data_migration_rds_max_capacity" {
#   description = "The maximum capacity for the RDS instance"
#   type        = number
# }

# variable "project" {
#   description = "Project Name"
#   type        = string
# }

# variable "environment" {
#   description = "Environment Name"
#   type        = string
# }

# variable "prefix" {
#   description = "Resource prefix"
#   type        = string
# }


variable "vpc_id" {
  description = "ID of the RDS vpc"
}
