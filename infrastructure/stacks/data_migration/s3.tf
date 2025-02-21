
module "migration_store_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${var.data_migration_project}-${var.migration_pipeline_store_bucket_name}-${var.environment}"
  versioning  = var.versioning
}

resource "aws_s3_bucket_policy" "migration_store_bucket_policy" {
  bucket = module.migration_store_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.migration_store_bucket_policy_document.json
}

data "aws_iam_policy_document" "migration_store_bucket_policy_document" {
  statement {
    sid     = "AllowSSLRequestsOnly"
    actions = ["s3:*"]
    resources = [
      module.migration_store_bucket.s3_bucket_arn,
    ]
    effect = "Deny"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}
