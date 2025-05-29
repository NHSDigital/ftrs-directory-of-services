module "s3" {
  # Module version: 4.9.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git?ref=1eb6a5766e0a84168d6e8aed2ccfa83e667a9561"

  bucket         = "${var.bucket_name}${local.workspace_suffix}"
  attach_policy  = var.attach_policy
  policy         = var.policy
  lifecycle_rule = var.lifecycle_rule_inputs

  force_destroy           = var.force_destroy
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
  # TODO Set up access logging bucket for CSOC
  #logging = {
  #  target_bucket = var.target_bucket
  #  target_prefix = var.target_prefix
  #}
  versioning = {
    enabled = var.versioning
  }
  website = var.website_map
}
