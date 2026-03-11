module "migration_store_bucket" {
  source            = "../../modules/s3"
  environment       = var.environment
  count             = local.is_primary_environment ? 1 : 0
  bucket_name       = "${local.resource_prefix}-${var.migration_pipeline_store_bucket_name}"
  versioning        = var.s3_versioning
  attach_policy     = true
  policy            = data.aws_iam_policy_document.migration_store_bucket_policy_document[0].json
  s3_logging_bucket = local.s3_logging_bucket

  lifecycle_rule_inputs = [
    {
      id      = "delete_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = "exports/"
      }
      expiration = {
        days = var.dynamodb_exports_s3_expiration_days
      }
    }
  ]
}

data "aws_iam_policy_document" "migration_store_bucket_policy_document" {
  count = local.is_primary_environment ? 1 : 0
  statement {
    principals {
      type = "AWS"
      identifiers = concat(
        local.env_sso_roles,
        [
          data.aws_iam_role.app_github_runner_iam_role.arn
        ]
      )
    }

    actions = [
      "s3:*",
    ]

    resources = [
      "_S3_BUCKET_ARN_",
      "_S3_BUCKET_ARN_/*",
    ]
  }
}
