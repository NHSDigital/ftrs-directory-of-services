module "ui_bucket" {
  source        = "../../modules/s3"
  bucket_name   = "${local.resource_prefix}-${var.ui_bucket_name}"
  versioning    = var.s3_versioning
  force_destroy = var.force_destroy
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

resource "aws_s3_bucket_policy" "ui_bucket_policy" {
  bucket = module.ui_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.ui_bucket_policy.json
}

data "aws_iam_policy_document" "ui_bucket_policy" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = ["s3:GetObject"]
    resources = [
      "${module.ui_bucket.s3_bucket_arn}/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values = [
        module.ui_cloudfront.cloudfront_distribution_arn,
      ]
    }
  }

  statement {
    principals {
      type = "AWS"
      identifiers = [
        data.aws_iam_role.app_github_runner_iam_role.arn,
        "arn:aws:iam::${data.aws_ssm_parameter.dos_aws_account_id_mgmt.value}:role/${var.repo_name}-${var.app_github_runner_role_name}"
      ]
    }

    actions = [
      "s3:*",
    ]

    resources = [
      "${module.ui_bucket.s3_bucket_arn}/*",
    ]
  }
}
