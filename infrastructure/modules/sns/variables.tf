variable "topic_name" {
  description = "Name of the SNS topic"
  type        = string
}

variable "display_name" {
  description = "Display name of the SNS topic"
  type        = string
}

variable "kms_key_id" {
  description = "KMS key ID for SNS topic encryption"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the SNS topic"
  type        = map(string)
  default     = {}
}

variable "subscriptions" {
  description = "Map of subscriptions (SQS, Lambda, etc.)"
  type        = map(any)
  default     = {}
}
