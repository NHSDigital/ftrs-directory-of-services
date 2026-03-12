variable "alarm_notification_email" {
  description = "List of email addresses to receive SNS notifications for Shield DDoS alarms"
  type        = list(string)
}

variable "emergency_contacts" {
  description = "List of emergency contacts for Proactive engagement from AWS Shield Advanced SRT"
  type = list(object({
    email_address = string
    phone_number  = string
    contact_notes = optional(string)
  }))
}

variable "isShieldProactiveEngagementEnabled" {
  description = "Whether to enable Proactive Engagement for AWS Shield Advanced"
  type        = bool
}

variable "isShieldSRTAccessEnabled" {
  description = "Whether to enable Shield Response Team (SRT) access"
  type        = bool
}

variable "isShieldAutomaticResponseEnabled" {
  description = "Whether to enable Automatic Application Layer DDoS mitigation"
  type        = bool
}

variable "cert_validation_record_ttl" {
  description = "The TTL of the DNS validation records for ACM certificates"
  type        = number
  default     = 60
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

variable "enable_warning_alarms" {
  description = "Enable actions for WARNING severity alarms (set to false to create placeholders)"
  type        = bool
  default     = true
}

variable "route53_health_check_failure_threshold" {
  description = "The number of consecutive health check failures before the health check is considered failed"
  type        = number
  default     = 3
}

variable "route53_health_check_request_interval" {
  description = "The interval in seconds between Route 53 health checks (10 or 30)"
  type        = number
  default     = 30
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
