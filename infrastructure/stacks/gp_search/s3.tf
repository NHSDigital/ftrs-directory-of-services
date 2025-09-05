module "s3" {
  source            = "../../modules/s3"
  bucket_name       = "${local.resource_prefix}-${var.s3_bucket_name}"
  force_destroy     = true
  s3_logging_bucket = local.s3_logging_bucket
}
