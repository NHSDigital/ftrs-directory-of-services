
module "migration_store_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${var.migration_pipeline_store_bucket_name}-${var.environment}"
  versioning  = false
}

resource "aws_s3_bucket_policy" "migration_store_bucket_policy" {
  bucket = module.migration_store_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.migration_store_bucket_policy_document.json
}

resource "aws_iam_role" "this" {
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "migration_store_bucket_policy_document" {
  statement {
    sid     = "AllowSSLRequestsOnly"
    actions = ["s3:*"]
    resources = [
      module.migration_store_bucket.s3_bucket_arn,
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

