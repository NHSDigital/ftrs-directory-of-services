variable "arn_to_protect" {
  description = "The arn to be protected with shield"
  type        = string
}

variable "resource_name" {
  description = "The resource name to be protected with shield"
  type        = string
}

variable "resource_prefix" {
  description = "The resource prefix for the resource protected with shield"
  type        = string
}

variable "health_check_association_arn" {
  description = "The health check ARN for association with Shield protection"
  type        = string
  default     = ""
}

variable "distribution_id_to_protect" {
  description = "Distribution Id to be protected with automatic DDoS mitigation"
  type        = string
}

variable "evaluation_period" {
  description = "The evaluation period for the CloudWatch alarm"
  default     = 20
  type        = string
}

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
  default     = false
}

variable "isShieldSRTAccessEnabled" {
  description = "Whether to enable Shield Response Team (SRT) access"
  type        = bool
  default     = false
}

variable "isShieldAutomaticResponseEnabled" {
  description = "Whether to enable Automatic Application Layer DDoS mitigation"
  type        = bool
  default     = false
}
