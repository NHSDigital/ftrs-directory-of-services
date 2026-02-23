module "backup_reports_bucket" {
  source            = "../../modules/s3"
  bucket_name       = "${local.resource_prefix}-reports"
  s3_logging_bucket = local.s3_logging_bucket

  lifecycle_rule_inputs = [
    {
      id      = "delete_logs_older_than_x_days"
      enabled = true
      filter = {
        prefix = ""
      }
      expiration = {
        days = var.backup_report_bucket_retention_days
      }
    }
  ]
}
