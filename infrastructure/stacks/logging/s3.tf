module "logging_bucket" {
  source      = "../../modules/s3"
  bucket_name = local.s3_logging_bucket
  versioning  = var.s3_logging_bucket_versioning

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

resource "aws_s3_bucket_policy" "logging_bucket_policy" {
  bucket = module.logging_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.logging_bucket_policy_document.json
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

    resources = ["${module.logging_bucket.s3_bucket_arn}/*"]
  }
}
