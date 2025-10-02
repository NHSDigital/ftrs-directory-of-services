variable "name" {
  description = "The name of the API Gateway"
  type        = string
}

variable "description" {
  description = "A description for the API Gateway"
  type        = string
}

variable "create_domain_name" {
  description = "Create a domain name(s) for the Gateway. If set to true, you'll need to pass through at least one domain name"
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "The domain name(s) to be associated with the Gateway"
  type        = string
}

variable "create_domain_records" {
  description = "Creates R53 records for the Gateway domains"
  type        = bool
  default     = true
}

variable "hosted_zone_name" {
  description = "The name of the hosted zone in which to spin up the R53 records"
  type        = string
}

variable "domain_certificate_arn" {
  description = "The ARN that points to the certificate in AWS associated with the Gateway domain"
  type        = string
}

variable "mtls_truststore_uri" {
  description = "A URI that points to the location of a truststore that holds the certificates and keys for the mTLS mechanism required for authentication between our APIM Proxy and API Backend"
  type        = string
}
variable "routes" {
  description = "A map of routes for the API Gateway and their integrations"
  type        = map(any)
}
