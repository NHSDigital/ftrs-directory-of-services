module "etl_ods_store_bucket" {
  source            = "../../modules/s3"
  bucket_name       = "${local.resource_prefix}-${var.etl_ods_pipeline_store_bucket_name}"
  versioning        = var.s3_versioning
  s3_logging_bucket = local.s3_logging_bucket
}
