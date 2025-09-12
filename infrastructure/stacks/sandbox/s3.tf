module "sandbox_store_bucket" {
  source            = "../../modules/s3"
  bucket_name       = "${local.resource_prefix}-${var.sndbox_pipeline_store_bucket_name}"
  versioning        = var.s3_versioning
  s3_logging_bucket = local.s3_logging_bucket
}

resource "aws_s3_bucket_policy" "sandbox_store_bucket_policy" {
  bucket = module.sandbox_store_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.sandbox_store_bucket_policy_document.json
}

data "aws_iam_policy_document" "sandbox_store_bucket_policy_document" {
  statement {
    sid     = "AllowSSLRequestsOnly"
    actions = ["s3:*"]
    resources = [
      module.sandbox_store_bucket.s3_bucket_arn,
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
