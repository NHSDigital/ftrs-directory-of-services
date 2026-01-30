module "s3" {
  # Module version: 5.7.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git?ref=c375418373496865e2770ad8aabfaf849d4caee5"

  bucket         = "${var.bucket_name}${local.workspace_suffix}"
  attach_policy  = var.attach_policy
  policy         = var.policy
  lifecycle_rule = var.lifecycle_rule_inputs

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

resource "aws_s3_bucket_policy" "enforce_kms_truststore" {
  count  = var.enable_kms_encryption ? 1 : 0
  bucket = module.s3.s3_bucket_id
  policy = jsonencode({ Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyUnencryptedUploads"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:PutObject"
        Resource  = "${module.s3.s3_bucket_arn}/*",
        Condition = {
          ArnNotEquals = {
            "s3:x-amz-server-side-encryption-aws-kms-key-id" : var.s3_encryption_key_arn # gitleaks:allow
          }
        }
      },
      {
        Sid       = "DenyUnencryptedUploadsKMS"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:PutObject"
        Resource  = "${module.s3.s3_bucket_arn}/*"
        Condition = {
          "StringNotEquals" : {
            "s3:x-amz-server-side-encryption" : "aws:kms"
          }
        }
      }
    ]
  })
}
