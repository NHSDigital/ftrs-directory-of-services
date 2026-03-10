module "metric_alarm" {
  for_each = local.alarms
  source   = "git::https://github.com/terraform-aws-modules/terraform-aws-cloudwatch.git//modules/metric-alarm?ref=a2a5f9d15e30d0d24b667933599e5e1bef24a8b8"

  alarm_name          = each.value.alarm_name
  comparison_operator = each.value.comparison_operator
  evaluation_periods  = each.value.evaluation_periods
  actions_enabled     = each.value.actions_enabled
  metric_name         = length(each.value.metric_queries) == 0 ? each.value.metric_name : null
  namespace           = length(each.value.metric_queries) == 0 ? each.value.namespace : null
  period              = length(each.value.metric_queries) == 0 ? each.value.period : null
  statistic           = length(each.value.metric_queries) == 0 ? (can(regex("^p(\\d+(\\.\\d+)?)$", each.value.statistic)) ? null : each.value.statistic) : null
  extended_statistic  = length(each.value.metric_queries) == 0 ? (can(regex("^p(\\d+(\\.\\d+)?)$", each.value.statistic)) ? each.value.statistic : null) : null
  threshold           = length(each.value.metric_queries) == 0 ? each.value.threshold : null
  alarm_description   = each.value.description
  alarm_actions       = [aws_sns_topic.alarms.arn]
  treat_missing_data  = "notBreaching"
  datapoints_to_alarm = each.value.datapoints_to_alarm
  metric_query        = each.value.metric_queries
  threshold_metric_id = each.value.threshold_metric_id

  dimensions = length(each.value.metric_queries) == 0 ? {
    (each.value.dimension_name) = each.value.resource_identifier
  } : null

  tags = merge(
    var.tags,
    {
      api_path = lookup(each.value, "api_path", "N/A")
      service  = lookup(each.value, "service", "Unknown")
    }
  )
}
