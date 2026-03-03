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
                LogGroup = aws_cloudwatch_log_group.dms_db_data_protection_audit_log_group[0].name
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
resource "aws_cloudwatch_log_group" "dms_db_data_protection_audit_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  # checkov:skip=CKV_AWS_338: Justification: Non-production do not require long term log retention.
  count = local.is_primary_environment ? 1 : 0

  name              = "/aws/data-protection-audit/${var.environment}/${local.resource_prefix}-${var.dms_db_lambda_name}"
  retention_in_days = var.dms_audit_cloudwatch_logs_retention_days
}

resource "aws_cloudwatch_metric_alarm" "dms_cdc_latency_source_critical" {
  # TODO restore after test
  # count = local.is_primary_environment ? 1 : 0

  alarm_name          = "DMS-CDCLatencySource-High"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 5
  metric_name         = "CDCLatencySource"
  namespace           = "AWS/DMS"
  period              = 60
  statistic           = "Average"
  threshold           = 120
  treat_missing_data  = "notBreaching"

  dimensions = {
    ReplicationTaskIdentifier = data.aws_dms_replication_task.dms_cdc_replication_task.id
  }

  alarm_description = "Critical - CDC latency on DMS source > 120 seconds"

  alarm_actions = [aws_sns_topic.data_migration_sns_topic.arn]
  ok_actions    = [aws_sns_topic.data_migration_sns_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "dms_cdc_latency_target_critical" {
  # TODO restore after test
  # count = local.is_primary_environment ? 1 : 0

  alarm_name          = "DMS-CDCLatencyTarget-High"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 5
  metric_name         = "CDCLatencyTarget"
  namespace           = "AWS/DMS"
  period              = 60
  statistic           = "Average"
  threshold           = 120
  treat_missing_data  = "notBreaching"

  dimensions = {
    ReplicationTaskIdentifier = data.aws_dms_replication_task.dms_cdc_replication_task.id
  }

  alarm_description = "Critical - CDC latency on DMS target > 120 seconds"

  alarm_actions = [aws_sns_topic.data_migration_sns_topic.arn]
  ok_actions    = [aws_sns_topic.data_migration_sns_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "dms_cdc_latency_source_warning" {
  # TODO restore after test
  # count = local.is_primary_environment ? 1 : 0

  alarm_name          = "${local.resource_prefix}-DMS-CDCLatencySource-Warning"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 5
  datapoints_to_alarm = 5
  metric_name         = "CDCLatencySource"
  namespace           = "AWS/DMS"
  period              = 60
  statistic           = "Average"
  threshold           = 30
  treat_missing_data  = "notBreaching"

  dimensions = {
    ReplicationTaskIdentifier = data.aws_dms_replication_task.dms_cdc_replication_task.id
  }

  alarm_description = "Warning - CDC latency on DMS source > 30 seconds"

  alarm_actions = [aws_sns_topic.data_migration_sns_topic.arn]
  ok_actions    = [aws_sns_topic.data_migration_sns_topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "dms_cdc_latency_target_warning" {
  # TODO restore after test

  alarm_name          = "${local.resource_prefix}-DMS-CDCLatencyTarget-Warning"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 5
  datapoints_to_alarm = 5
  metric_name         = "CDCLatencyTarget"
  namespace           = "AWS/DMS"
  period              = 60
  statistic           = "Average"
  threshold           = 30
  treat_missing_data  = "notBreaching"

  dimensions = {
    ReplicationTaskIdentifier = data.aws_dms_replication_task.dms_cdc_replication_task.id
  }

  alarm_description = "Warning - CDC latency on DMS target > 30 seconds"

  alarm_actions = [aws_sns_topic.data_migration_sns_topic.arn]
  ok_actions    = [aws_sns_topic.data_migration_sns_topic.arn]
}
