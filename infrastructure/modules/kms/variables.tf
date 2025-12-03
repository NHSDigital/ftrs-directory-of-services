variable "description" {
  description = "The description for the KMS key."
  type        = string
  default     = "KMS key managed by Terraform"
}

variable "kms_rotation_period_in_days" {
  description = "The number of days in the rotation period for the KMS key."
  type        = number
  default     = 365
}

variable "alias_name" {
  description = "The alias name for the KMS key."
  type        = string
  default     = ""
}

variable "account_id" {
  description = "The AWS account ID where the KMS key will be created."
  type        = string
  default     = ""
}

variable "aws_service_name" {
  description = "The AWS service name that will be allowed to use the KMS key."
  type        = list(string)
}

variable "enable_key_rotation" {
  description = "Whether to enable key rotation for the KMS key."
  type        = bool
  default     = true
}
