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

variable "waf_log_group_policy_name" {
  description = "The WAF log group policy name"
  type        = string
}

variable "osis_apigw_log_group_policy_name" {
  description = "The OSIS & API Gateway log group policy name"
  type        = string
}
