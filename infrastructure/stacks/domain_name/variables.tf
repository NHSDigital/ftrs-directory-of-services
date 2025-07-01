variable "root_domain_name" {
  description = "The root domain name for the project, used for DNS and other configurations"
  type        = string
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID for the domain"
  type        = string
}
