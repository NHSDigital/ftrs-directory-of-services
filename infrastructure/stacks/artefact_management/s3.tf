module "artefacts_bucket" {
  source            = "../../modules/s3"
  bucket_name       = local.artefacts_bucket
  attach_policy     = true
  policy            = data.aws_iam_policy_document.artefacts_bucket_policy.json
  s3_logging_bucket = local.s3_logging_bucket

  # Lifecycle rules work with tag-based retention strategy:
  # - Objects tagged "retention=ephemeral" expire per rules below
  # - Objects tagged "retention=retain" are kept (used for last X versions, see RETAIN_VERSIONS in Makefiles)
  # - Objects tagged "retention=permanent" are kept indefinitely (releases)
  lifecycle_rule_inputs = [
    {
      id     = "development-latest-retain-5-versions"
      status = "Enabled"
      filter = {
        prefix = "development/latest/"
      }
      noncurrent_version_expiration = {
        noncurrent_days           = 1
        newer_noncurrent_versions = 5
      }
    },
    {
      id     = "development-expire-30-days"
      status = "Enabled"
      filter = {
        prefix = "development/"
        tags = {
          retention = "ephemeral"
        }
      }
      expiration = {
        days = 30
      }
      noncurrent_version_expiration = {
        noncurrent_days = 10
      }
    },
    {
      id     = "staging-expire-90-days"
      status = "Enabled"
      filter = {
        prefix = "staging/"
        tags = {
          retention = "ephemeral"
        }
      }
      expiration = {
        days = 90
      }
      noncurrent_version_expiration = {
        noncurrent_days = 10
      }
    },
    {
      id     = "release-candidates-expire-90-days"
      status = "Enabled"
      filter = {
        prefix = "release-candidates/"
        tags = {
          retention = "ephemeral"
        }
      }
      expiration = {
        days = 90
      }
      noncurrent_version_expiration = {
        noncurrent_days = 10
      }
    }
  ]
}

data "aws_iam_policy_document" "artefacts_bucket_policy" {
  statement {
    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-FtRS-RW-Developer_b0ffd523c3b8ddb9",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-FtRS-RW-Infrastructure_e5f5de072b3e7cf8",
        "${data.aws_iam_role.app_github_runner_iam_role.arn}",
        "${data.aws_iam_role.account_github_runner_iam_role.arn}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_prod.value}:role/${var.repo_name}-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_prod.value}:role/${var.repo_name}-${var.account_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-ref-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-ref-${var.account_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-int-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-int-${var.account_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-test-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-test-${var.account_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/${var.repo_name}-dev-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/${var.repo_name}-dev-${var.account_github_runner_role_name}"
      ]
    }
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      "_S3_BUCKET_ARN_"
    ]
  }

  statement {
    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-FtRS-RW-Developer_b0ffd523c3b8ddb9",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-FtRS-RW-Infrastructure_e5f5de072b3e7cf8",
        "${data.aws_iam_role.app_github_runner_iam_role.arn}",
        "${data.aws_iam_role.account_github_runner_iam_role.arn}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_prod.value}:role/${var.repo_name}-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_prod.value}:role/${var.repo_name}-${var.account_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-ref-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-ref-${var.account_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-int-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-int-${var.account_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-test-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-test-${var.account_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/${var.repo_name}-dev-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/${var.repo_name}-dev-${var.account_github_runner_role_name}"
      ]
    }
    actions = [
      "s3:GetObject",
      "s3:GetObjectTagging",
      "s3:DeleteObject",
      "s3:PutObject",
      "s3:PutObjectTagging",
      "s3:GetObjectVersion"

    ]
    resources = [
      "_S3_BUCKET_ARN_/*",
    ]
  }
}
