variable "s3_bucket_id" {
  description = "The ID of the S3 bucket"
}

variable "s3_bucket_regional_domain_name" {
  description = "The regional domain name of the S3 bucket"
}

variable "comment" {
  description = "The default comment"
  default     = "S3 bucket distribution"
}

variable "default_root_object" {
  description = "The default root object"
  default     = "index.html"
}

variable "allowed_methods" {
  description = "allowed methods"
  default     = ["GET", "HEAD"]
}

variable "cached_methods" {
  description = "cached methods"
  default     = ["GET", "HEAD"]
}

variable "min_ttl" {
  description = "min ttl"
  default     = 0
}

variable "default_ttl" {
  description = "default ttl"
  default     = 3600
}

variable "max_ttl" {
  description = "max ttl"
  default     = 86400
}

variable "cloud_front_name" {
  description = "Name of the cloudfront instance"
}
