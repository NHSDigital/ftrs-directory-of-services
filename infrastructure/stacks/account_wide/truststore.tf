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
resource "aws_s3_object" "truststore_pem" {
  bucket = module.trust_store_s3_bucket.truststore.id
  key    = "mtls/truststore.pem"
  source = "truststore.pem" # Local path to truststore file
  etag   = filemd5("truststore.pem")
}
