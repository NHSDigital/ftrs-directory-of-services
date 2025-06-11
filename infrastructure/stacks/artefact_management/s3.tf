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
        "arn:aws:iam::${data.aws_caller_identity.current.id}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-PowerUser_f7f1ace556f4a062",
        "${data.aws_iam_role.app_github_runner_iam_role.arn}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/${var.repo_name}-${var.app_github_runner_role_name}"
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
        "arn:aws:iam::${data.aws_caller_identity.current.id}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-PowerUser_f7f1ace556f4a062",
        "${data.aws_iam_role.app_github_runner_iam_role.arn}",
        "arn:aws:iam::${data.aws_ssm_parameter.aws_account_id_dev.value}:role/${var.repo_name}-${var.app_github_runner_role_name}"
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
