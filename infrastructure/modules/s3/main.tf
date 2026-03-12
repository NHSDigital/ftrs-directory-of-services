module "s3" {
  # Module version: 5.8.2
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git?ref=c686a8b53be706e532c1d6845b08bd3895776ab0"

  bucket                                = local.bucket_name
  attach_policy                         = var.attach_policy || var.enable_kms_encryption
  policy                                = data.aws_iam_policy_document.combined_policy.json
  attach_deny_insecure_transport_policy = true
  lifecycle_rule                        = var.lifecycle_rule_inputs

  force_destroy                         = var.force_destroy
  block_public_acls                     = true
  block_public_policy                   = true
  ignore_public_acls                    = true
  restrict_public_buckets               = true
  attach_cloudtrail_log_delivery_policy = var.attach_cloudtrail_log_delivery_policy

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
    target_bucket = local.logging_bucket_name
    target_prefix = "${local.bucket_name}/"
  } : {}

  metric_configuration = var.metric_configuration_enabled ? [{
    name = "EntireBucket"
  }] : []

  versioning = {
    enabled = var.versioning
  }

  website = var.website_map
}


data "aws_iam_policy_document" "enforce_kms_truststore" {
  count = var.enable_kms_encryption ? 1 : 0
  statement {
    sid    = "DenyUnencryptedUploads"
    effect = "Deny"
    principals {
      identifiers = ["*"]
      type        = "*"
    }
    actions   = ["s3:PutObject"]
    resources = ["_S3_BUCKET_ARN_/*"]
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
    resources = ["_S3_BUCKET_ARN_/*"]
    condition {
      test     = "StringNotEquals"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["aws:kms"]
    }
  }
}

data "aws_iam_policy_document" "combined_policy" {
  source_policy_documents = compact([
    var.enable_kms_encryption ? data.aws_iam_policy_document.enforce_kms_truststore[0].json : "",
    var.attach_policy ? var.policy : ""
  ])
}
