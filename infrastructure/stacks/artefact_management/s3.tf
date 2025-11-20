module "artefacts_bucket" {
  source      = "../../modules/s3"
  bucket_name = local.artefacts_bucket
}


resource "aws_s3_bucket_policy" "artefacts_bucket_policy" {
  depends_on = [module.artefacts_bucket]
  bucket     = local.artefacts_bucket
  policy     = data.aws_iam_policy_document.artefacts_bucket_policy.json
}

data "aws_iam_policy_document" "artefacts_bucket_policy" {
  statement {
    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-FtRS-RW-Developer_b0ffd523c3b8ddb9",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-FtRS-RW-Infrastructure_e5f5de072b3e7cf8",
        "${data.aws_iam_role.app_github_runner_iam_role.arn}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_int.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_ref.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_prod.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}"
      ]
    }
    actions = [
      "s3:ListBucket",
    ]
    resources = [
      "${module.artefacts_bucket.s3_bucket_arn}"
    ]
  }

  statement {
    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-FtRS-RW-Developer_b0ffd523c3b8ddb9",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-FtRS-RW-Infrastructure_e5f5de072b3e7cf8",
        "${data.aws_iam_role.app_github_runner_iam_role.arn}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_int.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_ref.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_test.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_prod.value}:role/${var.repo_name}-*-${var.app_github_runner_role_name}"
      ]
    }
    actions = [
      "s3:GetObject",
      "s3:GetObjectTagging",
      "s3:DeleteObject",
      "s3:PutObject",
      "s3:PutObjectTagging"
    ]
    resources = [
      "${module.artefacts_bucket.s3_bucket_arn}/*",
    ]
  }
}
