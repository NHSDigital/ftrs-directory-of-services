module "sns" {
  source = "../sns"

  topic_name   = var.sns_topic_name
  display_name = var.sns_display_name
  kms_key_id   = var.kms_key_id

  tags = var.tags
}

module "cloudwatch_alarms" {
  for_each = local.alarms
  source   = "../cloudwatch-alarm"

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
  function_name       = each.value.dimension_name == "FunctionName" ? each.value.resource_identifier : null
  workspace_suffix    = var.workspace_suffix
  namespace           = each.value.namespace
  treat_missing_data  = "notBreaching"
}
