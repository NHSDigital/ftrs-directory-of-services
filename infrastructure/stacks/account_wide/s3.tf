# VPC Flow Logs S3 Bucket and Resource Policy
module "vpc_flow_logs_s3_bucket" {
  source        = "../../modules/s3"
  bucket_name   = "${local.resource_prefix}-${var.vpc_flow_logs_bucket_name}"
  versioning    = var.flow_log_s3_versioning
  force_destroy = var.flow_log_s3_force_destroy
  lifecycle_rule_inputs = [
    {
      id      = "delete_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = ""
      }
      expiration = {
        days = var.flow_logs_s3_expiration_days
      }
    }
  ]
  s3_logging_bucket = local.s3_logging_bucket
}

resource "aws_s3_bucket_policy" "vpc_flow_logs_s3_bucket_policy" {
  bucket = module.vpc_flow_logs_s3_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.vpc_flow_logs_s3_bucket_policy_doc.json
}

data "aws_iam_policy_document" "vpc_flow_logs_s3_bucket_policy_doc" {
  statement {
    sid = "AWSLogDeliveryWrite"

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    actions = ["s3:PutObject"]

    resources = ["${module.vpc_flow_logs_s3_bucket.s3_bucket_arn}/*"]
  }

  statement {
    sid = "AWSLogDeliveryAclCheck"

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    actions = ["s3:GetBucketAcl"]

    resources = [module.vpc_flow_logs_s3_bucket.s3_bucket_arn]
  }
}

# Subnet Flow Logs S3 Bucket and Resource Policy
module "subnet_flow_logs_s3_bucket" {
  source        = "../../modules/s3"
  bucket_name   = "${local.resource_prefix}-${var.subnet_flow_logs_bucket_name}"
  versioning    = var.flow_log_s3_versioning
  force_destroy = var.flow_log_s3_force_destroy
  lifecycle_rule_inputs = [
    {
      id      = "delete_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = ""
      }
      expiration = {
        days = var.flow_logs_s3_expiration_days
      }
    }
  ]
}

resource "aws_s3_bucket_policy" "subnet_flow_logs_s3_bucket_policy" {
  bucket = module.subnet_flow_logs_s3_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.subnet_flow_logs_s3_bucket_policy_doc.json
}

data "aws_iam_policy_document" "subnet_flow_logs_s3_bucket_policy_doc" {
  statement {
    sid = "AWSLogDeliveryWrite"

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    actions = ["s3:PutObject"]

    resources = ["${module.subnet_flow_logs_s3_bucket.s3_bucket_arn}/*"]
  }

  statement {
    sid = "AWSLogDeliveryAclCheck"

    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    actions = ["s3:GetBucketAcl"]

    resources = [module.subnet_flow_logs_s3_bucket.s3_bucket_arn]
  }
}

module "trust_store_s3_bucket" {
  # This module creates an S3 bucket for the trust store used for MTLS Certificates.
  source            = "../../modules/s3"
  bucket_name       = local.s3_trust_store_bucket_name
  s3_logging_bucket = local.s3_logging_bucket
}

# Bucket to store migration pipeline data
module "migration_store_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${local.resource_prefix}-${var.migration_pipeline_store_bucket_name}"
  versioning  = var.s3_versioning

  lifecycle_rule_inputs = [
    {
      id      = "delete_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = "exports/"
      }
      expiration = {
        days = var.dynamodb_exports_s3_expiration_days
      }
    }
  ]
}

resource "aws_s3_bucket_policy" "migration_store_bucket_policy" {
  bucket = module.migration_store_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.migration_store_bucket_policy_document.json
}

data "aws_iam_policy_document" "migration_store_bucket_policy_document" {
  statement {
    principals {
      type = "AWS"
      identifiers = concat(
        local.env_sso_roles,
        [
          data.aws_iam_role.app_github_runner_iam_role.arn
        ]
      )
    }

    actions = [
      "s3:*",
    ]

    resources = [
      module.migration_store_bucket.s3_bucket_arn,
      "${module.migration_store_bucket.s3_bucket_arn}/*",
    ]
  }
}


