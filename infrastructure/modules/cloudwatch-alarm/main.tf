module "metric_alarm" {
  # Module version: 5.7.2
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-cloudwatch.git?ref=a2a5f9d15e30d0d24b667933599e5e1bef24a8b8"

  alarm_name          = "${var.alarm_name}${var.workspace_suffix}"
  comparison_operator = var.comparison_operator
  evaluation_periods  = var.evaluation_periods
  actions_enabled     = var.actions_enabled
  metric_name         = var.metric_name
  namespace           = var.namespace
  period              = var.period
  statistic           = can(regex("^p(\\d+(\\.\\d+)?)$", var.statistic)) ? null : var.statistic
  extended_statistic  = can(regex("^p(\\d+(\\.\\d+)?)$", var.statistic)) ? var.statistic : null
  threshold           = var.threshold
  alarm_description   = var.alarm_description
  alarm_actions       = [var.sns_topic_arn]
  treat_missing_data  = var.treat_missing_data

  dimensions = {
    FunctionName = var.function_name
  }

  tags = {
    Name = "${var.alarm_name}${var.workspace_suffix}"
  }
}
