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
variable "referenced_security_group_id" {
  description = "Ref Security Group ID"
}

variable "ip_protocol" {
  description = "ip protocol"
}

variable "create_subnet_group" {
  description = "Bol value to create subnet group or not"
  type        = bool
  default     = false
}

variable "create_security_group" {
  description = "Bol value to create security group or not"
  type        = bool
  default     = false
}
variable "manage_master_user_password" {
  description = "Manage maser user password"
  type        = bool
  default     = false
}
variable "master_username" {
  description = "Username for RDS"
  type        = string
}

variable "master_password" {
  description = "Password for RDS"
  type        = string
}

variable "rds_min_capacity" {
  description = "Serverless RDS Scalability min capacity"
  type        = number
  default     = 1
}
variable "rds_max_capacity" {
  description = "Serverless RDS Scalability max capacity"
  type        = number
  default     = 1
}
variable "skip_final_snapshot" {
  description = "Determines whether a final snapshot is created before the cluster is deleted."
  type        = bool
  default     = false
}
