variable "splunk_hec_app_token_name" {
  description = "The name of the Secrets Manager secret to store the Splunk HEC token for application logging"
  type        = string
  default     = "splunk_hec_app_token"
}

variable "splunk_hec_endpoint_app" {
  description = "Splunk HEC endpoint (no trailing slash)"
  type        = string
}

variable "splunk_hec_token_app" {
  description = "Splunk HEC token"
  type        = string
  sensitive   = true
}

variable "firehose_name" {
  type    = string
  default = "splunk-firehose"
}

variable "enable_firehose_s3_kms_encryption" {
  description = "Whether to enable KMS encryption for S3 buckets"
  type        = bool
  default     = false
}

variable "splunk_collector_url" {
  description = "The Splunk HEC collector base URL - minus hec endpoint"
  type        = string
}

variable "firehose_logs_retention_in_days" {
  description = "Number of days to retain Firehose logs in CloudWatch Log Group"
  type        = number
  default     = 14
}
# TODO remove default when moving to account wide stack
variable "firehose_error_log_group_name" {
  description = "The name of the CloudWatch Log Group to store Firehose error logs"
  type        = string
  default     = "firehose-error-log-group"
}
