module "s3" {
  source      = "../../modules/s3"
  bucket_name = "${local.resource_prefix}-${var.s3_bucket_name}"
}
