module "trust_store_s3_bucket" {
  # This module creates an S3 bucket for the trust store used for MTLS Certificates.
  source      = "../../modules/s3"
  bucket_name = "${local.account_prefix}-${var.s3_trust_store_bucket_name}"
}
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = module.trust_store_s3_bucket.s3_bucket_arn

  versioning_configuration {
    status = "Enabled"
  }
}
