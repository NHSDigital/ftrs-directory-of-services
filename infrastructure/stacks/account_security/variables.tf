variable "enable_iam_analyzer" {
  description = "Enable IAM Access Analyzer for the account"
  type        = bool
  default     = false
}

variable "analyzer_findings_log_group_retention_days" {
  description = "Number of days to retain Access Analyzer findings in CloudWatch Logs"
  type        = number
  default     = 30
}
