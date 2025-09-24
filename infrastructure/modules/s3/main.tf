module "s3" {
  # Module version: 5.7.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git?ref=c375418373496865e2770ad8aabfaf849d4caee5"

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

  logging = var.s3_logging_bucket != "" ? {
    target_bucket = var.s3_logging_bucket
    target_prefix = "${var.bucket_name}${local.workspace_suffix}/"
  } : {}

  versioning = {
    enabled = var.versioning
  }

  website = var.website_map
}
