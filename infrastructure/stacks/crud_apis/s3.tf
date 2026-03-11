module "crud_apis_bucket" {
  source            = "../../modules/s3"
  environment       = var.environment
  bucket_name       = "${local.resource_prefix}-${var.crud_apis_store_bucket_name}"
  versioning        = var.s3_versioning
  s3_logging_bucket = local.s3_logging_bucket
}
