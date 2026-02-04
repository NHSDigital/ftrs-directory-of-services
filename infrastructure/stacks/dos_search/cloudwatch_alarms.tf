module "cloudwatch_alarms" {
  for_each = local.alarms
  source   = "../../modules/cloudwatch-alarm"

  alarm_name          = each.value.alarm_name
  comparison_operator = each.value.comparison_operator
  evaluation_periods  = each.value.evaluation_periods
  actions_enabled     = each.value.actions_enabled
  metric_name         = each.value.metric_name
  period              = each.value.period
  statistic           = each.value.statistic
  threshold           = each.value.threshold
  alarm_description   = each.value.description
  sns_topic_arn       = module.sns.topic_arn
  function_name       = each.value.function_name
  workspace_suffix    = local.workspace_suffix
  namespace           = "AWS/Lambda"
  treat_missing_data  = "notBreaching"
}
