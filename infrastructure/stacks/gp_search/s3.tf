module "s3" {
  source      = "../../modules/s3"
  bucket_name = "${var.project}-${var.environment}-${var.s3_bucket_name}"
}
