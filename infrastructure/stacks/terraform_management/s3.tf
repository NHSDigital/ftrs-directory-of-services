module "terraform_state_bucket" {
  source      = "../../modules/s3"
  bucket_name = var.terraform_state_bucket_name
}
