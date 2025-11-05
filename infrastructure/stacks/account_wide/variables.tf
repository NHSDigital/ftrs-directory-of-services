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

variable "waf_name" {
  description = "The Web ACL name for WAF"
  type        = string
}

variable "waf_scope" {
  description = "The scope for WAF"
  type        = string
}

variable "waf_log_group" {
  description = "Name for the WAF Web ACL log group"
  type        = string
}
variable "waf_log_group_class" {
  description = "The log group class for WAF"
  type        = string
}

variable "waf_log_group_name_prefix" {
  description = "Prefix for WAF CloudWatch Log Group Name"
  type        = string
  default     = "aws-waf-logs-"
}

variable "waf_log_group_retention_days" {
  description = "The retention period for the Read only viewer Web ACL Log group"
  type        = number
  default     = 365
}

# Performance EC2 configuration
variable "performance_instance_type" {
  description = "EC2 instance type for performance testing"
  type        = string
  default     = "t3.small"
}

variable "performance_ami_name_pattern" {
  description = "List of AMI name patterns to match for the performance EC2 (e.g., AL2023)"
  type        = list(string)
  default     = ["al2023-ami-*-x86_64"]
}

variable "performance_ami_architectures" {
  description = "List of acceptable CPU architectures for the performance EC2 AMI"
  type        = list(string)
  default     = ["x86_64"]
}

variable "performance_volume_size" {
  description = "Root EBS volume size (GiB) for the performance instance"
  type        = number
  default     = 30
  validation {
    condition     = var.performance_volume_size >= 30
    error_message = "performance_volume_size must be >= 30 GiB to satisfy the AMI snapshot minimum size"
  }
}

variable "performance_version" {
  description = "Apache JMeter version to install"
  type        = string
  default     = "5.6.3"
}

variable "performance_poweroff_after_setup" {
  description = "Whether to power off the instance after installing JMeter"
  type        = bool
  default     = true
}

variable "performance_jwt_dependency_version" {
  description = "Version of java-jwt library to download"
  type        = string
  default     = "4.5.0"
}

