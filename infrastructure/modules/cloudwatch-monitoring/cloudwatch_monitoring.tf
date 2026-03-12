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
  alarm_actions       = [var.external_sns_topic_arn != null ? var.external_sns_topic_arn : aws_sns_topic.alarms[0].arn]
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
