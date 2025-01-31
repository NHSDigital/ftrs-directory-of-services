# ==============================================================================
# Mandatory variables

variable "table_name" { description = "The table name of the DynamoDB" }

# ==============================================================================
# Default variables

variable "hash_key" {
  default = "id"
}
variable "autoscaling_enabled" {
  default = true
}
variable "stream_enabled" {
  default = true
}
variable "stream_view_type" {
  default = "NEW_AND_OLD_IMAGES"
}
variable "attributes" {
  default = [{
    name = "id"
    type = "S"
  }]
}
