module "ui_bucket" {
  count             = local.stack_enabled
  source            = "../../modules/s3"
  bucket_name       = "${local.resource_prefix}-${var.ui_bucket_name}"
  versioning        = var.s3_versioning
  force_destroy     = var.force_destroy
  attach_policy     = true
  policy            = data.aws_iam_policy_document.ui_bucket_policy[0].json
  s3_logging_bucket = local.s3_logging_bucket
  lifecycle_rule_inputs = [
    {
      id                                     = "delete_old_release_versions"
      enabled                                = true
      abort_incomplete_multipart_upload_days = 7
      filter = {
        prefix = ""
      }
      noncurrent_version_expiration = {
        noncurrent_days           = 30,
        newer_noncurrent_versions = 2
      }
    }
  ]
}

data "aws_iam_policy_document" "ui_bucket_policy" {
  count = local.stack_enabled
  statement {
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = ["s3:GetObject"]
    resources = [
      "_S3_BUCKET_ARN_/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values = [
        module.ui_cloudfront[0].cloudfront_distribution_arn,
      ]
    }
  }

  statement {
    principals {
      type = "AWS"
      identifiers = [
        data.aws_iam_role.app_github_runner_iam_role[0].arn,
        "arn:aws:iam::${data.aws_ssm_parameter.dos_aws_account_id_mgmt[0].value}:role/${var.repo_name}-${var.app_github_runner_role_name}"
      ]
    }

    actions = [
      "s3:*",
    ]

    resources = [
      "_S3_BUCKET_ARN_/*",
    ]
  }
}
