module "s3" {
  source      = "../../modules/s3"
  bucket_name = "${var.project}-${var.environment}-${s3_bucket_name}"
}
