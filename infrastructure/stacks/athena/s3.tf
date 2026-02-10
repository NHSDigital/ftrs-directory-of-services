module "athena_spill_bucket" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  source      = "../../modules/s3"
  bucket_name = "${local.resource_prefix}-spill"

  lifecycle_rule_inputs = [
    {
      id      = "delete_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = ""
      }
      expiration = {
        days = var.athena_spill_bucket_retention_days
      }
    }
  ]
}

module "athena_output_bucket" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  source                = "../../modules/s3"
  bucket_name           = "${local.resource_prefix}-output"
  enable_kms_encryption = true
  s3_encryption_key_arn = data.aws_kms_key.s3_kms_key[0].arn

  lifecycle_rule_inputs = [
    {
      id      = "delete_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = ""
      }
      expiration = {
        days = var.athena_output_bucket_retention_days
      }
    }
  ]
}

