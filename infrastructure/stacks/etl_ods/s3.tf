module "etl_ods_store_bucket" {
  source            = "../../modules/s3"
  bucket_name       = "${local.resource_prefix}-${var.etl_ods_pipeline_store_bucket_name}"
  versioning        = var.s3_versioning
  s3_logging_bucket = local.s3_logging_bucket
  attach_policy     = true
  policy            = data.aws_iam_policy_document.etl_ods_store_bucket_policy_document.json
}

data "aws_iam_policy_document" "etl_ods_store_bucket_policy_document" {
  statement {
    sid     = "AllowSSLRequestsOnly"
    actions = ["s3:*"]
    resources = [
      "_S3_BUCKET_ARN_"
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
