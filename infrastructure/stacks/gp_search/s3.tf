module "s3" {
  source      = "../../modules/s3"
  bucket_name = var.gp_search_bucket_name
}
