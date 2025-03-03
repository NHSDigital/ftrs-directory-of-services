module "migration_store_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${var.project}-${var.temp_test_bucket_name}-${var.environment}"
}

