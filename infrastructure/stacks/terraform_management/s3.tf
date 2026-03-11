module "terraform_state_bucket" {
  source            = "../../modules/s3"
  environment       = var.environment
  bucket_name       = var.terraform_state_bucket_name
  s3_logging_bucket = local.s3_logging_bucket
  depends_on        = [module.logging_bucket]
}

module "logging_bucket" {
  source        = "../../modules/s3"
  environment   = var.environment
  bucket_name   = local.s3_logging_bucket
  versioning    = var.s3_logging_bucket_versioning
  attach_policy = true
  policy        = data.aws_iam_policy_document.logging_bucket_policy_document.json

  lifecycle_rule_inputs = [
    {
      id      = "delete_s3_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = ""
      }
      expiration = {
        days = var.s3_logging_expiration_days
      }
    }
  ]
}

data "aws_iam_policy_document" "logging_bucket_policy_document" {
  statement {
    principals {
      identifiers = ["logging.s3.amazonaws.com"]
      type        = "Service"
    }

    actions = [
      "s3:PutObject",
    ]

    resources = ["_S3_BUCKET_ARN_/*"]
  }
}
