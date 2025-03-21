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
        "arn:aws:iam::${data.aws_caller_identity.current.id}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-Developer_8bdf3f98a2591a2b",
        "${aws_iam_role.github_runner_iam_role.arn}",
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
        "arn:aws:iam::${data.aws_caller_identity.current.id}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/AWSReservedSSO_DOS-Developer_8bdf3f98a2591a2b",
      "${aws_iam_role.github_runner_iam_role.arn}", ]
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
