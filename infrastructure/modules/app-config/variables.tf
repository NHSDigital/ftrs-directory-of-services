variable "name" {
  description = "The name of the AppConfig application."
  type        = string
}

variable "description" {
  description = "The description of the AppConfig application."
  type        = string
}

variable "config_profile_type" {
  description = "The type of the configuration profile."
  type        = string
  default     = "AWS.AppConfig.FeatureFlags"
}

variable "hosted_config_version_content_type" {
  description = "The content type of the hosted configuration version."
  type        = string
  default     = "application/json"
}

variable "hosted_config_version_content" {
  description = "The json file path for the hosted configuration version."
  type        = string
}

variable "environments" {
  description = "A map of environment configurations. Each environment should have 'name' and 'description' fields."
  type = map(object({
    name        = string
    description = string
  }))
  default = {}
}

variable "create_iam_policy" {
  description = "Whether to create the IAM policy granting AppConfig data access."
  type        = bool
  default     = true
}

variable "iam_policy_name" {
  description = "Optional custom name for the IAM policy; defaults to '<name>-appconfig-data-read'."
  type        = string
  default     = null
}

variable "iam_policy_description" {
  description = "Optional custom description for the IAM policy."
  type        = string
  default     = null
}

variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
  default     = "eu-west-2"
}
