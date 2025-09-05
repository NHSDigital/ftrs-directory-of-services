variable "enable_nat_gateway" {
  description = "Whether to create a NAT Gateway for the VPC"
  type        = bool
}

variable "single_nat_gateway" {
  description = "Whether to use a single NAT Gateway in the VPC"
  type        = bool
}

variable "one_nat_gateway_per_az" {
  description = "Whether to create only one NAT Gateway per AZ"
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

variable "create_database_internet_gateway_route" {
  description = "Whether to create an internet gateway route for public database access"
  type        = bool
}

variable "create_database_nat_gateway_route" {
  description = "Whether to create a NAT gateway route for the database"
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

variable "gateway_vpc_endpoint_type" {
  description = "The VPC enpoint type"
  type        = string
  default     = "Gateway"
}

variable "database_dedicated_network_acl" {
  description = "Whether to use dedicated network ACL (not default) and custom rules for database subnets"
  type        = bool
}

variable "private_dedicated_network_acl" {
  description = "Whether to use dedicated network ACL (not default) and custom rules for private subnets"
  type        = bool
}

variable "public_dedicated_network_acl" {
  description = "Whether to use dedicated network ACL (not default) and custom rules for public subnets"
  type        = bool
}

variable "flow_log_destination_type" {
  description = "THe destination type for the flow logs"
  type        = string
}

variable "flow_log_file_format" {
  description = "The file format for the flow logs"
  type        = string
}

variable "vpc_flow_logs_bucket_name" {
  description = "The VPC Flow logs bucket name"
  type        = string
}

variable "subnet_flow_logs_bucket_name" {
  description = "The Subnet Flow logs bucket name"
  type        = string
}

variable "flow_log_s3_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
}

variable "flow_log_s3_force_destroy" {
  description = "Whether to forcefully destroy the bucket when it contains objects"
  type        = bool
  default     = false
}

variable "flow_logs_s3_expiration_days" {
  description = "The number of days before the VPC flow logs are deleted"
  type        = number
}

variable "s3_logging_bucket_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
}

variable "vpc" {
  description = "A map of VPC configuration, including VPC ID, CIDR block, and other networking details"
  type        = map(any)
  default     = {}
}

variable "enable_flow_log" {
  description = "Whether VPC Flow logs are enabled or not"
  type        = bool
  default     = false
}

variable "s3_logging_expiration_days" {
  description = "The number of days before the S3 access logs are deleted"
  type        = number
  default     = 30
}
