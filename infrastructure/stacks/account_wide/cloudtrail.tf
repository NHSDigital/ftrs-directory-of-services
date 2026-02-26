# CloudTrail trail logging S3 object-level data events
# trivy:ignore:AVD-AWS-0014
resource "aws_cloudtrail" "s3_data_events" {
  # checkov:skip=CKV_AWS_252: Justification: No SNS required at the moment
  # checkov:skip=CKV2_AWS_10: Justification: CloudWatch Logs integration is not required for this S3 data events trail.
  # checkov:skip=CKV_AWS_67: We are only enabling S3 object-level data events and don't need all regions to be enabled.
  name = "${local.resource_prefix}-${var.cloudtrail_trail_name}"

  s3_bucket_name = module.cloudtrail_s3_bucket.s3_bucket_id

  # Regional, non-aggregated trail (same region delivery, no multi-region)
  is_multi_region_trail         = false
  include_global_service_events = false

  # Requirement: log file validation
  enable_log_file_validation = true

  # Enable KMS encryption
  kms_key_id = module.cloudtrail_encryption_key.arn

  # S3 object-level write events — satisfies [S3.22]
  advanced_event_selector {
    name = "Log S3 object-level write events (S3.22)"

    field_selector {
      field  = "eventCategory"
      equals = ["Data"]
    }

    field_selector {
      field  = "resources.type"
      equals = ["AWS::S3::Object"]
    }

    field_selector {
      field  = "readOnly"
      equals = ["false"]
    }

    # Exclude the CloudTrail delivery bucket itself to prevent a feedback loop
    field_selector {
      field           = "resources.ARN"
      not_starts_with = ["${module.cloudtrail_s3_bucket.s3_bucket_arn}/"]
    }
  }

  # S3 object-level read events — satisfies [S3.23]
  advanced_event_selector {
    name = "Log S3 object-level read events (S3.23)"

    field_selector {
      field  = "eventCategory"
      equals = ["Data"]
    }

    field_selector {
      field  = "resources.type"
      equals = ["AWS::S3::Object"]
    }

    field_selector {
      field  = "readOnly"
      equals = ["true"]
    }

    # Exclude the CloudTrail delivery bucket itself to prevent a feedback loop
    field_selector {
      field           = "resources.ARN"
      not_starts_with = ["${module.cloudtrail_s3_bucket.s3_bucket_arn}/"]
    }
  }
}
