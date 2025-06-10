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

variable "opensearch_type" {
  description = "The type of OpenSearch"
  type        = string
}

variable "opensearch_standby_replicas" {
  description = "Number of standby replicas for OpenSearch"
  type        = string
}

variable "opensearch_create_access_policy" {
  description = "Flag to create access policy for OpenSearch"
  type        = bool
}

variable "opensearch_create_network_policy" {
  description = "Flag to create network policy for OpenSearch"
  type        = bool
}

variable "opensearch_collection_name" {
  description = "The OpenSearch Collection name"
  type        = string
}

variable "s3_trust_store_bucket_name" {
  description = "The name of the S3 bucket for the trust store used for MTLS Certificates"
  type        = string
}

variable "root_domain_name" {
  description = "The root domain name for the project, used for DNS and other configurations"
  type        = string
}
