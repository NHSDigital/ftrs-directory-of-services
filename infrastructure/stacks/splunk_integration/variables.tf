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

# variable "log_groups" {
#   type = set(string)
#   default = [
#     "/aws/lambda/service-a",
#     "/aws/lambda/service-b",
#     "/aws/ec2/app"
#   ]
# }
