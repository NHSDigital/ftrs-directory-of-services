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

resource "aws_cloudwatch_metric_alarm" "dms_metric_alarms" {
  # TODO restore after test
  # count = local.is_primary_environment ? 1 : 0
  for_each = merge(local.dms_simple_metric_alarm_configs, local.dms_metric_query_alarm_configs)

  alarm_name          = each.value.alarm_name
  comparison_operator = try(each.value.comparison_operator, try(each.value.threshold_metric_id, null) != null ? "GreaterThanUpperThreshold" : "GreaterThanThreshold")
  evaluation_periods  = each.value.evaluation_periods
  datapoints_to_alarm = each.value.datapoints_to_alarm
  metric_name         = length(try(each.value.metric_queries, [])) > 0 ? null : try(each.value.metric_name, null)
  namespace           = length(try(each.value.metric_queries, [])) > 0 ? null : try(each.value.namespace, "AWS/DMS")
  period              = length(try(each.value.metric_queries, [])) > 0 ? null : each.value.period
  statistic           = length(try(each.value.metric_queries, [])) > 0 ? null : try(each.value.statistic, "Average")
  threshold           = try(each.value.threshold, null)
  threshold_metric_id = try(each.value.threshold_metric_id, null)
  treat_missing_data  = "notBreaching"

  insufficient_data_actions = []

  dynamic "metric_query" {
    for_each = try(each.value.metric_queries, [])
    content {
      id          = metric_query.value.id
      expression  = try(metric_query.value.expression, null)
      label       = try(metric_query.value.label, null)
      return_data = try(metric_query.value.return_data, null)

      dynamic "metric" {
        for_each = try(metric_query.value.metric, null) == null ? [] : [metric_query.value.metric]
        content {
          metric_name = metric.value.metric_name
          namespace   = metric.value.namespace
          period      = metric.value.period
          stat        = metric.value.stat
          unit        = try(metric.value.unit, null)
          dimensions  = try(metric.value.dimensions, null)
        }
      }
    }
  }

  dimensions = length(try(each.value.metric_queries, [])) > 0 ? null : try(each.value.dimensions, {
    ReplicationTaskIdentifier = data.aws_dms_replication_task.dms_cdc_replication_task.id
  })

  alarm_description = each.value.alarm_description

  alarm_actions = [aws_sns_topic.data_migration_sns_topic.arn]
  ok_actions    = [aws_sns_topic.data_migration_sns_topic.arn]
}
