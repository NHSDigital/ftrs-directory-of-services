# ==============================================================================
# Mandatory variables

variable "table_name" {
  description = "The name of the DynamoDB table."
  type        = string
}

# ==============================================================================
# Default variables

variable "hash_key" {
  description = "The primary key for the DynamoDB table."
  type        = string
  default     = "id"
}

variable "range_key" {
  description = "The range key for the DynamoDB table."
  type        = string
  default     = null
}

variable "autoscaling_enabled" {
  description = "Flag to enable or disable auto-scaling for the table."
  type        = bool
  default     = true
}

variable "stream_enabled" {
  description = "Flag to enable or disable DynamoDB Streams."
  type        = bool
  default     = false
}

variable "stream_view_type" {
  description = "Determines the information written to the stream when an item is modified."
  type        = string
  default     = "NEW_AND_OLD_IMAGES"
}

variable "attributes" {
  description = "List of attributes with their names and data types."
  type = list(object({
    name = string
    type = string
  }))
  default = [{
    name = "id"
    type = "S"
  }]
}

variable "billing_mode" {
  description = "Specifies the billing mode for DynamoDB (PROVISIONED or PAY_PER_REQUEST)."
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "point_in_time_recovery_enabled" {
  description = "Enable or disable point-in-time recovery for the DynamoDB table"
  type        = bool
  default     = false
}

variable "global_secondary_indexes" {
  type = list(object({
    name               = string
    hash_key           = string
    range_key          = optional(string)
    projection_type    = string
    non_key_attributes = optional(list(string))
  }))
  default = []
}
