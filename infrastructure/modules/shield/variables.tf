variable "arns_to_protect" {
  description = "Map of name to arn to be protected with shield"
  type        = map(string)
  default     = {}
}

variable "health_check_associations" {
  description = "Map of resource name to health check ARN for association with Shield protection"
  type        = map(string)
  default     = {}
}

variable "distribution_ids_to_protect" {
  description = "List of Distribution Ids to be protected with automatic DDoS mitigation"
  type        = list(string)
  default     = []
}

variable "evaluation_period" {
  description = "The evaluation period for the CloudWatch alarm"
  default     = 20
  type        = string
}

variable "resource_prefix" {
  description = "The prefix to use for resource names"
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
  default = []
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
