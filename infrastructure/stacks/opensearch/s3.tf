data "aws_iam_policy_document" "ddb_export_policy" {
  statement {
    sid    = "DynamoDBExportAccess"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:PutObjectAcl"
    ]
    resources = ["arn:aws:s3:::${local.resource_prefix}-${var.ddb_export_bucket_name}/*"]
    principals {
      type        = "Service"
      identifiers = ["dynamodb.amazonaws.com"]
    }
  }
}
module "s3" {
  count             = local.stack_enabled
  source            = "../../modules/s3"
  bucket_name       = "${local.resource_prefix}-${var.ddb_export_bucket_name}"
  versioning        = var.s3_versioning
  force_destroy     = true
  s3_logging_bucket = local.s3_logging_bucket
  attach_policy     = true
  policy            = data.aws_iam_policy_document.ddb_export_policy.json
}

data "aws_iam_policy_document" "s3_opensearch_pipeline_dlq_bucket_policy" {
  statement {
    sid    = "PipelineAccess"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:PutObjectAcl"
    ]
    resources = ["arn:aws:s3:::${local.resource_prefix}-${var.opensearch_pipeline_s3_dlq_bucket_name}/*"]
    principals {
      type        = "Service"
      identifiers = ["osis-pipelines.amazonaws.com"]
    }
  }
}
module "s3_opensearch_pipeline_dlq_bucket" {
  count         = local.stack_enabled
  source        = "../../modules/s3"
  bucket_name   = "${local.resource_prefix}-${var.opensearch_pipeline_s3_dlq_bucket_name}"
  versioning    = var.s3_versioning
  force_destroy = true
  attach_policy = true
  policy        = data.aws_iam_policy_document.s3_opensearch_pipeline_dlq_bucket_policy.json
}
