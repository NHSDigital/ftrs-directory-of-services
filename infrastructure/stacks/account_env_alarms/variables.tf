variable "truststore_s3_5xx_errors_warning_alarm_threshold" {
  description = "The 5xx errors count threshold for triggering a warning alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_5xx_errors_critical_alarm_threshold" {
  description = "The 5xx errors count threshold for triggering a critical alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_4xx_errors_warning_alarm_threshold" {
  description = "The 4xx errors count threshold for triggering a warning alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_4xx_errors_critical_alarm_threshold" {
  description = "The 4xx errors count threshold for triggering a critical alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_5xx_errors_warning_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the 5xx errors warning alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_5xx_errors_critical_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the 5xx errors critical alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_4xx_errors_warning_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the 4xx errors warning alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_4xx_errors_critical_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the 4xx errors critical alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_5xx_errors_warning_alarm_period" {
  description = "The period (in seconds) for the 5xx errors warning alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_5xx_errors_critical_alarm_period" {
  description = "The period (in seconds) for the 5xx errors critical alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_4xx_errors_warning_alarm_period" {
  description = "The period (in seconds) for the 4xx errors warning alarm for the truststore S3 bucket"
  type        = number
}

variable "truststore_s3_4xx_errors_critical_alarm_period" {
  description = "The period (in seconds) for the 4xx errors critical alarm for the truststore S3 bucket"
  type        = number
}

variable "enable_warning_alarms" {
  description = "Enable actions for WARNING severity alarms (set to false to create placeholders)"
  type        = bool
  default     = false
}

variable "terraform_state_s3_5xx_errors_warning_alarm_threshold" {
  description = "The 5xx errors count threshold for triggering a warning alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_5xx_errors_critical_alarm_threshold" {
  description = "The 5xx errors count threshold for triggering a critical alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_4xx_errors_warning_alarm_threshold" {
  description = "The 4xx errors count threshold for triggering a warning alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_4xx_errors_critical_alarm_threshold" {
  description = "The 4xx errors count threshold for triggering a critical alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_5xx_errors_warning_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the 5xx errors warning alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_5xx_errors_critical_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the 5xx errors critical alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_4xx_errors_warning_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the 4xx errors warning alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_4xx_errors_critical_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the 4xx errors critical alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_5xx_errors_warning_alarm_period" {
  description = "The period (in seconds) for the 5xx errors warning alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_5xx_errors_critical_alarm_period" {
  description = "The period (in seconds) for the 5xx errors critical alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_4xx_errors_warning_alarm_period" {
  description = "The period (in seconds) for the 4xx errors warning alarm for the terraform state S3 bucket"
  type        = number
}

variable "terraform_state_s3_4xx_errors_critical_alarm_period" {
  description = "The period (in seconds) for the 4xx errors critical alarm for the terraform state S3 bucket"
  type        = number
}

variable "vpce_active_connections_warning_alarm_threshold" {
  description = "The active connections count threshold for triggering a warning alarm for VPC endpoints"
  type        = number
}

variable "vpce_active_connections_critical_alarm_threshold" {
  description = "The active connections count threshold for triggering a critical alarm for VPC endpoints"
  type        = number
}

variable "vpce_active_connections_warning_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the active connections warning alarm for VPC endpoints"
  type        = number
}

variable "vpce_active_connections_critical_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the active connections critical alarm for VPC endpoints"
  type        = number
}

variable "vpce_active_connections_warning_alarm_period" {
  description = "The period (in seconds) for the active connections warning alarm for VPC endpoints"
  type        = number
}

variable "vpce_active_connections_critical_alarm_period" {
  description = "The period (in seconds) for the active connections critical alarm for VPC endpoints"
  type        = number
}

variable "acm_days_to_expiry_warning_alarm_threshold" {
  description = "The days to expiry threshold for triggering a warning alarm for ACM certificates"
  type        = number
  default     = 30
}

variable "acm_days_to_expiry_critical_alarm_threshold" {
  description = "The days to expiry threshold for triggering a critical alarm for ACM certificates"
  type        = number
  default     = 15
}

variable "acm_days_to_expiry_warning_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the days to expiry warning alarm for ACM certificates"
  type        = number
}

variable "acm_days_to_expiry_critical_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the days to expiry critical alarm for ACM certificates"
  type        = number
}

variable "acm_days_to_expiry_warning_alarm_period" {
  description = "The period (in seconds) for the days to expiry warning alarm for ACM certificates"
  type        = number
}

variable "acm_days_to_expiry_critical_alarm_period" {
  description = "The period (in seconds) for the days to expiry critical alarm for ACM certificates"
  type        = number
}

variable "route53_health_check_status_critical_alarm_threshold" {
  description = "The health check status threshold for triggering a critical alarm (0 = unhealthy)"
  type        = number
  default     = 1
}

variable "route53_health_check_status_critical_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the health check status critical alarm"
  type        = number
}

variable "route53_health_check_status_critical_alarm_period" {
  description = "The period (in seconds) for the health check status critical alarm"
  type        = number
}

variable "route53_health_check_percentage_healthy_critical_alarm_threshold" {
  description = "The percentage healthy threshold for triggering a critical alarm"
  type        = number
  default     = 100
}

variable "route53_health_check_percentage_healthy_critical_alarm_evaluation_periods" {
  description = "The number of evaluation periods for the health check percentage healthy critical alarm"
  type        = number
}

variable "route53_health_check_percentage_healthy_critical_alarm_period" {
  description = "The period (in seconds) for the health check percentage healthy critical alarm"
  type        = number
}

variable "sns_topic_name" {
  description = "Name of the SNS topic for alarms"
  type        = string
}
