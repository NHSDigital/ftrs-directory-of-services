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
  bucket_name   = local.s3_log_bucket
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

module "logging_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${local.resource_prefix}-${var.s3_logging_bucket_name}"
  versioning  = var.s3_versioning
}

resource "aws_s3_bucket_policy" "logging_bucket_policy" {
  bucket = module.logging_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.logging_bucket_policy_document.json
}

data "aws_iam_policy_document" "logging_bucket_policy_document" {
  statement {
    principals {
      identifiers = ["logging.s3.amazonaws.com"]
      type        = "Service"
    }

    actions = [
      "s3:PutObject",
    ]

    resources = ["${module.logging_bucket.s3_bucket_arn}/*"]
  }
}
