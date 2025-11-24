resource "aws_accessanalyzer_analyzer" "account_analyzer" {
  count         = var.enable_iam_analyzer ? 1 : 0
  analyzer_name = "${local.resource_prefix}-account-analyzer"
  type          = "ACCOUNT"
}

resource "aws_cloudwatch_log_group" "access_analyzer_findings" {
  count             = var.enable_iam_analyzer ? 1 : 0
  name              = "/aws/accessanalyzer/${local.resource_prefix}-access-analyzer-findings"
  retention_in_days = var.analyzer_findings_log_group_retention_days
}

resource "aws_cloudwatch_event_rule" "access_analyzer_findings" {
  count       = var.enable_iam_analyzer ? 1 : 0
  name        = "${local.resource_prefix}-access-analyzer-findings"
  description = "Capture IAM Access Analyzer findings for external access patterns"

  event_pattern = jsonencode({
    source      = ["aws.access-analyzer"]
    detail-type = ["Access Analyzer Finding"]
    detail = {
      status = ["ACTIVE"]
    }
  })
}

resource "aws_cloudwatch_event_target" "access_analyzer_to_logs" {
  count     = var.enable_iam_analyzer ? 1 : 0
  rule      = aws_cloudwatch_event_rule.access_analyzer_findings[0].name
  target_id = "SendToCloudWatchLogs"
  arn       = aws_cloudwatch_log_group.access_analyzer_findings[0].arn
}

resource "aws_cloudwatch_log_metric_filter" "access_analyzer_critical_findings" {
  count          = var.enable_iam_analyzer ? 1 : 0
  name           = "${local.resource_prefix}-access-analyzer-critical"
  log_group_name = aws_cloudwatch_log_group.access_analyzer_findings[0].name
  pattern        = "{ $.detail.status = \"ACTIVE\" && $.detail.resourceType != \"AWS::IAM::Role\" }"

  metric_transformation {
    name      = "AccessAnalyzerCriticalFindings"
    namespace = "CustomSecurity"
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_metric_alarm" "access_analyzer_critical" {
  count               = var.enable_iam_analyzer ? 1 : 0
  alarm_name          = "${local.resource_prefix}-access-analyzer-critical-findings"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "AccessAnalyzerCriticalFindings"
  namespace           = "CustomSecurity"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alert on new IAM Access Analyzer critical findings"
  treat_missing_data  = "notBreaching"
}
