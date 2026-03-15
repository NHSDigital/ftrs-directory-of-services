module "metric_alarm" {
  for_each = local.alarms
  source   = "git::https://github.com/terraform-aws-modules/terraform-aws-cloudwatch.git//modules/metric-alarm?ref=a2a5f9d15e30d0d24b667933599e5e1bef24a8b8"

  alarm_name          = each.value.alarm_name
  comparison_operator = each.value.comparison_operator
  evaluation_periods  = each.value.evaluation_periods
  actions_enabled     = each.value.actions_enabled
  metric_name         = each.value.metric_name
  namespace           = each.value.namespace
  period              = each.value.period
  statistic           = can(regex("^p(\\d+(\\.\\d+)?)$", each.value.statistic)) ? null : each.value.statistic
  extended_statistic  = can(regex("^p(\\d+(\\.\\d+)?)$", each.value.statistic)) ? each.value.statistic : null
  threshold           = each.value.threshold
  alarm_description   = each.value.description
  alarm_actions       = [aws_sns_topic.alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = each.value.dimensions

  tags = merge(
    var.tags,
    {
      api_path = lookup(each.value, "api_path", "N/A")
      service  = lookup(each.value, "service", "Unknown")
    }
  )
}

resource "aws_cloudwatch_log_metric_filter" "rate_limiting_429" {
  count = var.api_gateway_log_group_name != null ? 1 : 0

  name           = "${var.resource_prefix}-429-rate-limited-requests"
  log_group_name = var.api_gateway_log_group_name
  pattern        = "{ $.context.status = 429 }"

  metric_transformation {
    name      = var.rate_limiting_429_metric_name
    namespace = var.rate_limiting_429_metric_namespace
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_metric_alarm" "rate_limiting_429_critical" {
  count = var.rate_limiting_429_critical_threshold != null ? 1 : 0

  alarm_name          = "${var.resource_prefix}-api-429-rate-limiting-critical"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.rate_limiting_429_critical_evaluation_periods
  metric_name         = var.rate_limiting_429_metric_name
  namespace           = var.rate_limiting_429_metric_namespace
  period              = var.rate_limiting_429_critical_period
  statistic           = "Sum"
  threshold           = var.rate_limiting_429_critical_threshold
  alarm_description   = "API Gateway 429 rate limiting critical threshold - customers are being rate-limited"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  treat_missing_data  = "notBreaching"

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "rate_limiting_429_warning" {
  count = var.rate_limiting_429_warning_threshold != null && var.enable_warning_alarms ? 1 : 0

  alarm_name          = "${var.resource_prefix}-api-429-rate-limiting-warning"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = var.rate_limiting_429_warning_evaluation_periods
  metric_name         = var.rate_limiting_429_metric_name
  namespace           = var.rate_limiting_429_metric_namespace
  period              = var.rate_limiting_429_warning_period
  statistic           = "Sum"
  threshold           = var.rate_limiting_429_warning_threshold
  alarm_description   = "API Gateway 429 rate limiting warning threshold - sustained rate limiting detected"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  treat_missing_data  = "notBreaching"

  tags = var.tags
}
