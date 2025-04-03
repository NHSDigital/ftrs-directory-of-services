module "s3" {
  source      = "../../modules/s3"
  bucket_name = "${var.project}-s3-${var.environment}"
}
