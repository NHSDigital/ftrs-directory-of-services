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


variable "etl_ods_pipeline_store_bucket_name" {
  description = "The name of the S3 bucket to use for the etl ods pipeline"
}

variable "s3_versioning" {
  description = "Whether to enable versioning on the S3 bucket"
  type        = bool
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

variable "apim_url" {
  description = "The URL of the API Management instance"
  type        = string
  default     = "https://int.api.service.nhs.uk/dos-ingest/FHIR/R4"
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
