module "migration_store_bucket" {
  source      = "../../modules/s3"
  count       = local.is_primary_environment ? 1 : 0
  bucket_name = "${local.resource_prefix}-${var.migration_pipeline_store_bucket_name}"
  versioning  = var.s3_versioning

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

resource "aws_s3_bucket_policy" "migration_store_bucket_policy" {
  count  = local.is_primary_environment ? 1 : 0
  bucket = module.migration_store_bucket[0].s3_bucket_id
  policy = data.aws_iam_policy_document.migration_store_bucket_policy_document[0].json
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
      module.migration_store_bucket[0].s3_bucket_arn,
      "${module.migration_store_bucket[0].s3_bucket_arn}/*",
    ]
  }
}
