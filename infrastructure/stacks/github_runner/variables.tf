variable "github_org" {
  description = "The name of the git hub organisation - eg NHSDigital"
  type        = string
}

variable "oidc_provider_url" {
  description = "URL of oidc provider"
  type        = string
}

variable "oidc_client" {
  description = "Client of oidc provider"
  type        = string
}

variable "oidc_thumbprint" {
  description = "Thumbprint for oidc provider"
  type        = string
}
