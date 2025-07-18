module "trust_store_s3_bucket" {
  # This module creates an S3 bucket for the trust store used for MTLS Certificates.
  source      = "../../modules/s3"
  bucket_name = local.s3_trust_store_bucket_name
}
