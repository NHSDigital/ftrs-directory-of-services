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

variable "create_database_route_table" {
  description = "Whether to create a database route table for RDS"
  type        = bool
}

variable "log_group_retention_in_days" {
  description = "Number of days to retain logs"
  default     = 7
}
