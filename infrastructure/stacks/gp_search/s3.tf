module "s3" {
  source      = "../../modules/s3"
  bucket_name = "${var.project}-${var.gp_search_bucket_name}-${var.environment}"
}
