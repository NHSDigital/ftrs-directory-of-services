variable "project" {
  description = "The project code, typically reflecting a sub-project of the project owner"
}

variable "project_owner" {
  description = "The owner of the project, based on organisation and department codes"
}

variable "team_owner" {
  description = "The sub-team responsible for the stack"
}

variable "environment" {
  description = "The deployment environment e.g. dev, test, pre-prod, or prod"
}

variable "repo_name" {
  description = "The name of the GitHub repository associated with this project"
}

variable "service" {
  description = "The service or program that this project is associated with"
  type        = string
}

variable "cost_centre" {
  description = "The cost center used for consolidated billing and cost attribution to programs"
  type        = string
}

variable "data_classification" {
  description = "The data classification according to the Cloud Risk Model, enabling quick searches e.g. Low, Medium, High"
  type        = string
}

variable "data_type" {
  description = "The type of data handled by this project e.g. None, PCD, PII, Anonymized, UserAccount, Audit"
  type        = string
}

variable "project_type" {
  description = "The purpose of the resources e.g PoC, Pilot, Production"
  type        = string
}

variable "public_facing" {
  description = "Indicates if the project is accessible publicly via the internet"
  type        = string
}

variable "service_category" {
  description = "Identifies the service category to prioritize responses"
  type        = string
}

variable "artefacts_bucket_name" {
  description = "Artefacts S3 bucket name"
  type        = string
}

variable "account_github_runner_role_name" {
  description = "GitHub runner IAM role name for account"
  type        = string
  default     = "account-github-runner"
}

variable "app_github_runner_role_name" {
  description = "GitHub runner IAM role name for app"
  type        = string
  default     = "app-github-runner"
}

variable "stack_name" {
  description = "The hyphenated version of the stack name used in names of resources defined in that stack"
  type        = string
}

variable "dynamodb_table_names" {
  description = "List of DynamoDB table names"
  type        = list(string)
}

variable "vpc" {
  description = "A map of VPC configuration, including VPC ID, CIDR block, and other networking details"
  type        = map(any)
  default     = {}
}

variable "aws_accounts" {
  description = "List of AWS account environments"
  type        = list(string)
}

variable "mgmt_account_id" {
  description = "Management account ID"
  type        = string
}

variable "root_domain_name" {
  description = "Root domain name for the project"
  type        = string
}

variable "s3_trust_store_bucket_name" {
  description = "The name of the S3 bucket for the trust store used for MTLS Certificates"
  type        = string
}

variable "sso_roles" {
  description = "List of SSO roles for the environment"
  type        = list(string)
  default     = []
}

variable "gp_search_organisation_table_name" {
  description = "The dynamodb table name for gp search"
  type        = string
}

variable "dms_replication_instance_class" {
  description = "The instance class for the DMS replication instance"
  type        = string
  default     = null
}

variable "dms_engine" {
  description = "The engine for the DMS replication instance"
  type        = string
  default     = null
}

variable "dms_allocated_storage" {
  description = "The allocated storage for the DMS replication instance"
  type        = number
  default     = null
}

variable "full_migration_type" {
  description = "The type of migration for DMS"
  type        = string
  default     = null
}

variable "cdc_migration_type" {
  description = "The type of migration for DMS"
  type        = string
  default     = null
}

variable "dms_instance_multi_az" {
  description = "Is DMS instance set up in multi-AZ mode"
  type        = bool
  default     = false
}

variable "dms_task_logging_enabled" {
  description = "Enable logging for DMS tasks"
  type        = bool
  default     = true
}

variable "enable_flow_log" {
  description = "Whether VPC Flow logs are enabled or not"
  type        = bool
  default     = false
}

variable "dns_port" {
  description = "The port for DNS queries"
  type        = number
  default     = 53
}

variable "https_port" {
  description = "The port for HTTPS traffic"
  type        = number
  default     = 443
}
