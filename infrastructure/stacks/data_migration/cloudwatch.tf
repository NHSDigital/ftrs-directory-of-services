resource "aws_cloudwatch_log_data_protection_policy" "dms_db_protection_policy" {
  count = local.is_primary_environment ? 1 : 0

  log_group_name = module.dms_db_lambda[0].lambda_cloudwatch_log_group_name

  policy_document = jsonencode({
    Name    = "DmsDbLogDataProtectionPolicy"
    Version = "2021-06-01"
    Configuration = {
      CustomDataIdentifier = [
        { "Name" : "DMSUserPassword", "Regex" : "(?i)password\\s*[:=]\\s*['\"](.*?)['\"]" }
      ]
    }
    Statement = [
      {
        Sid = "Audit"
        DataIdentifier = [
          "DMSUserPassword"
        ]
        Operation = {
          Audit = {
            FindingsDestination = {
              CloudWatchLogs = {
                LogGroup = aws_cloudwatch_log_group.data_protection_audit_log_group[0].name
              }
            }
          }
        }
      },
      {
        Sid = "Redact"
        DataIdentifier = [
          "DMSUserPassword"
        ]
        Operation = {
          Deidentify = {
            MaskConfig = {}
          }
        }
      }
    ]
  })
}

# Create CloudWatch log group for audit logs
resource "aws_cloudwatch_log_group" "data_protection_audit_log_group" {
  count = local.is_primary_environment ? 1 : 0

  name              = "/aws/data-protection-audit/${var.environment}/${local.resource_prefix}-${var.dms_db_lambda_name}"
  retention_in_days = var.cloudwatch_log_retention_days
}
