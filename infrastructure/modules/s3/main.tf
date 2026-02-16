module "s3" {
  # Module version: 5.7.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git?ref=c375418373496865e2770ad8aabfaf849d4caee5"

  bucket                                = "${var.bucket_name}${local.workspace_suffix}"
  attach_policy                         = var.attach_policy || var.enable_kms_encryption
  policy                                = data.aws_iam_policy_document.combined_policy.json
  attach_deny_insecure_transport_policy = true
  lifecycle_rule                        = var.lifecycle_rule_inputs

  force_destroy           = var.force_destroy
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  server_side_encryption_configuration = var.enable_kms_encryption ? {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = var.s3_encryption_key_arn # gitleaks:allow
      }
    }
    } : {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }

  logging = var.s3_logging_bucket != "" ? {
    target_bucket = var.s3_logging_bucket
    target_prefix = "${var.bucket_name}${local.workspace_suffix}/"
  } : {}

  versioning = {
    enabled = var.versioning
  }

  website = var.website_map
}


data "aws_iam_policy_document" "enforce_kms_truststore" {
  statement {
    sid    = "DenyUnencryptedUploads"
    effect = "Deny"
    principals {
      identifiers = ["*"]
      type        = "*"
    }
    actions   = ["s3:PutObject"]
    resources = ["${module.s3.s3_bucket_arn}/*"]
    condition {
      test     = "ArnNotEquals"
      variable = "s3:x-amz-server-side-encryption-aws-kms-key-id"
      values   = [var.s3_encryption_key_arn] # gitleaks:allow
    }
  }
  statement {
    sid    = "DenyUnencryptedUploadsKMS"
    effect = "Deny"
    principals {
      identifiers = ["*"]
      type        = "*"
    }
    actions   = ["s3:PutObject"]
    resources = ["${module.s3.s3_bucket_arn}/*"]
    condition {
      test     = "StringNotEquals"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["aws:kms"]
    }
  }
}

data "aws_iam_policy_document" "combined_policy" {
  source_policy_documents = compact([
    var.enable_kms_encryption ? data.aws_iam_policy_document.enforce_kms_truststore.json : "",
    var.attach_policy ? var.policy : ""
  ])
}
