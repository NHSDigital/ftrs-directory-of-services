variable "project" {
  description = "The project code, typically reflecting a sub-project of the project owner"
}

variable "project_owner" {
  description = "The owner of the project, based on organisation and department codes"
}

variable "environment" {
  description = "The deployment environment e.g. dev, test, pre-prod, or prod"
}

variable "repo_name" {
  description = "The name of the GitHub repository associated with this project"
}

variable "tag_version" {
  description = "The version of the tagging policy in use, enabling evolution of the tagging strategy and supporting automation"
  type        = string
}

variable "service" {
  description = "The service or program that this project is associated with"
  type        = string
}

variable "cost_centre" {
  description = "The cost center used for consolidated billing and cost attribution to programs"
  type        = string
}

variable "data_classification" {
  description = "The data classification according to the Cloud Risk Model, enabling quick searches e.g. Low, Medium, High"
  type        = string
}

variable "data_type" {
  description = "The type of data handled by this project e.g. None, PCD, PII, Anonymized, UserAccount, Audit"
  type        = string
}

variable "project_type" {
  description = "The purpose of the resources e.g PoC, Pilot, Production"
  type        = string
}

variable "public_facing" {
  description = "Indicates if the project is accessible publicly via the internet"
  type        = string
}

variable "service_category" {
  description = "Identifies the service category to prioritize responses"
  type        = string
}

variable "on_off_pattern" {
  description = "Defines the automated schedule for turning resources on/off, applicable for non-production environments"
  type        = string
}
