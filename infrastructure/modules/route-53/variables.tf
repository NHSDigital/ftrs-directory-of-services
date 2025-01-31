variable "zone_name" {
  description = "The name of the hosted zone"
  type        = string
}

variable "comment" {
  description = "A comment for the hosted zone"
  type        = string
  default     = ""
}
