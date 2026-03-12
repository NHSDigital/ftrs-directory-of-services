variable "lambda_runtime" {
  description = "The runtime environment for the Lambda function"
}

variable "extractor_name" {
  description = "The name of the ETL ODS Extractor Lambda function"
}

variable "transformer_name" {
  description = "The name of the ETL ODS Transformer Lambda function"
}

variable "consumer_name" {
  description = "The name of the ETL ODS Consumer Lambda function"
}

variable "extractor_lambda_handler" {
  description = "The handler for the ETL ODS Extractor Lambda function"
  type        = string
}

variable "transformer_lambda_handler" {
  description = "The handler for the ETL ODS Transformer Lambda function"
  type        = string
}

variable "consumer_lambda_handler" {
  description = "The handler for the ETL ODS Consumer Lambda function"
  type        = string
}

variable "consumer_lambda_connection_timeout" {
  description = "The timeout for the ETL ODS consumer lambda function"
  type        = number
}


variable "extractor_lambda_connection_timeout" {
  description = "The timeout for the ETL ODS extractor lambda function. 12 minutes to allow for longer processing times"
  type        = number
}

variable "transformer_lambda_connection_timeout" {
  description = "The timeout for the ETL ODS transformer lambda function"
  type        = number
}

variable "lambda_memory_size" {
  description = "The memory size for the ETL ODS Lambda functions"
  type        = number
}

variable "delay_seconds" {
  description = "The number of seconds a message should be invisible to consumers"
}

variable "visibility_timeout_seconds" {
  description = "How long a message remains invisible to other consumers after being received by one consumer"
}

variable "max_message_size" {
  description = "The maximum size of the message"
}

variable "message_retention_seconds" {
  description = "How long the SQS queue keeps a message"
}

variable "receive_wait_time_seconds" {
  description = "Time period that a request could wait for a message to become available in the sqs queue"
}

variable "max_receive_count" {
  description = "The maximum number of times a message can be received before being sent to the dead letter queue"
}

variable "apim_base_url" {
  description = "The base URL of the API Management instance (without API path)"
  type        = string
  default     = "https://int.api.service.nhs.uk"
}

variable "apim_dos_ingest_path_segment" {
  description = "The path segment for APIM URL construction"
  type        = string
  default     = "dos-ingest"
}

variable "ods_url" {
  description = "The URL of the ODS Terminology API"
  type        = string
  default     = "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
}

variable "extractor_lambda_logs_retention" {
  description = "The number of days to retain logs for the extractor lambda"
  type        = number
  default     = 14
}

variable "transformer_lambda_logs_retention" {
  description = "The number of days to retain logs for the transformer lambda"
  type        = number
  default     = 14
}

variable "consumer_lambda_logs_retention" {
  description = "The number of days to retain logs for the consumer lambda"
  type        = number
  default     = 14
}

variable "ods_api_page_limit" {
  description = "The maximum number of organisations to retrieve per page from the ODS API"
  type        = number
  default     = 1000
}

################################################################################
# Lambda CloudWatch Alarms Configuration
################################################################################

############################
# Global / Shared
############################
variable "lambda_alarm_evaluation_periods" {
  description = "Default number of periods over which to evaluate alarms (unless overridden per metric/severity)"
  type        = number
  default     = 2
}

variable "lambda_alarm_period_seconds" {
  description = "Default CloudWatch period in seconds for alarm metric evaluation (Lambda metrics are 60s by default)"
  type        = number
  default     = 60
}

variable "lambda_throttles_evaluation_periods" {
  description = "Number of periods to evaluate for Lambda throttle alarms"
  type        = number
  default     = 1
}

variable "lambda_throttles_period_seconds" {
  description = "Period in seconds for Lambda throttle alarm evaluation"
  type        = number
  default     = 60
}

variable "invocations_spike_period_seconds" {
  description = "CloudWatch period in seconds for invocations spike alarm (e.g., 300s = 5min window)"
  type        = number
  default     = 300
}

variable "enable_warning_alarms" {
  description = "Enable actions for WARNING severity alarms (set to false to create placeholders)"
  type        = bool
  default     = true
}

############################
# EXTRACTOR LAMBDA
# Duration (Execution Time)
# CRITICAL: p99 > 30s
# WARNING: p95 > 25s
############################
variable "extractor_duration_p95_warning_ms" {
  description = "Extractor Lambda duration p95 warning threshold in milliseconds"
  type        = number
  default     = 25000
}

variable "extractor_duration_p99_critical_ms" {
  description = "Extractor Lambda duration p99 critical threshold in milliseconds"
  type        = number
  default     = 30000
}

############################
# EXTRACTOR LAMBDA
# Errors
# CRITICAL: > 5
# WARNING: > 3
############################
variable "extractor_errors_warning_threshold" {
  description = "Extractor Lambda errors WARNING threshold"
  type        = number
  default     = 3
}

variable "extractor_errors_critical_threshold" {
  description = "Extractor Lambda errors CRITICAL threshold"
  type        = number
  default     = 5
}

############################
# EXTRACTOR LAMBDA
# Throttles (Capacity Rejections)
# CRITICAL: > 0 for 1 minute
############################
variable "extractor_throttles_critical_threshold" {
  description = "Extractor Lambda throttles CRITICAL threshold (set to 0, alarm if > 0)"
  type        = number
  default     = 0
}

############################
# EXTRACTOR LAMBDA
# Concurrency (In-Flight Load)
# CRITICAL: >= 5
# WARNING: >= 3
############################
variable "extractor_concurrent_executions_warning" {
  description = "Extractor Lambda concurrency warning threshold"
  type        = number
  default     = 3
}

variable "extractor_concurrent_executions_critical" {
  description = "Extractor Lambda concurrency critical threshold"
  type        = number
  default     = 5
}

############################
# EXTRACTOR LAMBDA
# Invocations (Workload Volume)
# CRITICAL: > 10 (daily scheduled + manual triggers)
############################
variable "extractor_invocations_spike_critical" {
  description = "Extractor Lambda invocations spike CRITICAL threshold"
  type        = number
  default     = 10
}

############################
# TRANSFORMER LAMBDA
# Duration (Execution Time)
# CRITICAL: p99 > 60s
# WARNING: p95 > 50s
############################
variable "transformer_duration_p95_warning_ms" {
  description = "Transformer Lambda duration p95 warning threshold in milliseconds"
  type        = number
  default     = 50000
}

variable "transformer_duration_p99_critical_ms" {
  description = "Transformer Lambda duration p99 critical threshold in milliseconds"
  type        = number
  default     = 60000
}

############################
# TRANSFORMER LAMBDA
# Errors
# CRITICAL: > 20
# WARNING: > 10
############################
variable "transformer_errors_warning_threshold" {
  description = "Transformer Lambda errors WARNING threshold"
  type        = number
  default     = 10
}

variable "transformer_errors_critical_threshold" {
  description = "Transformer Lambda errors CRITICAL threshold"
  type        = number
  default     = 20
}

############################
# TRANSFORMER LAMBDA
# Throttles (Capacity Rejections)
# CRITICAL: > 0 for 1 minute
############################
variable "transformer_throttles_critical_threshold" {
  description = "Transformer Lambda throttles CRITICAL threshold (set to 0, alarm if > 0)"
  type        = number
  default     = 0
}

############################
# TRANSFORMER LAMBDA
# Concurrency (In-Flight Load)
# CRITICAL: >= 5
# WARNING: >= 4
############################
variable "transformer_concurrent_executions_warning" {
  description = "Transformer Lambda concurrency warning threshold"
  type        = number
  default     = 4
}

variable "transformer_concurrent_executions_critical" {
  description = "Transformer Lambda concurrency critical threshold"
  type        = number
  default     = 5
}

############################
# TRANSFORMER LAMBDA
# Invocations (Workload Volume)
# CRITICAL: > 2000 (2x baseline ~1000 orgs per ETL run)
############################
variable "transformer_invocations_spike_critical" {
  description = "Transformer Lambda invocations spike CRITICAL threshold"
  type        = number
  default     = 2000
}

############################
# CONSUMER LAMBDA
# Duration (Execution Time)
# CRITICAL: p99 > 45s
# WARNING: p95 > 40s
############################
variable "consumer_duration_p95_warning_ms" {
  description = "Consumer Lambda duration p95 warning threshold in milliseconds"
  type        = number
  default     = 40000
}

variable "consumer_duration_p99_critical_ms" {
  description = "Consumer Lambda duration p99 critical threshold in milliseconds"
  type        = number
  default     = 45000
}

############################
# CONSUMER LAMBDA
# Errors
# CRITICAL: > 20
# WARNING: > 10
############################
variable "consumer_errors_warning_threshold" {
  description = "Consumer Lambda errors WARNING threshold"
  type        = number
  default     = 10
}

variable "consumer_errors_critical_threshold" {
  description = "Consumer Lambda errors CRITICAL threshold"
  type        = number
  default     = 20
}

############################
# CONSUMER LAMBDA
# Throttles (Capacity Rejections)
# CRITICAL: > 0 for 1 minute
############################
variable "consumer_throttles_critical_threshold" {
  description = "Consumer Lambda throttles CRITICAL threshold (set to 0, alarm if > 0)"
  type        = number
  default     = 0
}

############################
# CONSUMER LAMBDA
# Concurrency (In-Flight Load)
# CRITICAL: >= 5
# WARNING: >= 4
############################
variable "consumer_concurrent_executions_warning" {
  description = "Consumer Lambda concurrency warning threshold"
  type        = number
  default     = 4
}

variable "consumer_concurrent_executions_critical" {
  description = "Consumer Lambda concurrency critical threshold"
  type        = number
  default     = 5
}

############################
# CONSUMER LAMBDA
# Invocations (Workload Volume)
# CRITICAL: > 2000 (2x baseline)
############################
variable "consumer_invocations_spike_critical" {
  description = "Consumer Lambda invocations spike CRITICAL threshold"
  type        = number
  default     = 2000
}

############################
# SQS Queue Alarms
############################
variable "transform_queue_age_threshold_seconds" {
  description = "Threshold in seconds for Transform Queue message age alarm"
  type        = number
  default     = 3600
}

variable "load_queue_age_threshold_seconds" {
  description = "Threshold in seconds for Load Queue message age alarm"
  type        = number
  default     = 3600
}
