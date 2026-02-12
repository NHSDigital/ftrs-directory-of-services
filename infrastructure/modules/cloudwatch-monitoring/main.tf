module "sns" {
  source = "../sns"

  topic_name   = var.sns_topic_name
  display_name = var.sns_display_name
  kms_key_id   = var.kms_key_id

  tags = var.tags
}

locals {
  # Support both template names and custom paths
  config_path = contains(["minimal", "standard", "comprehensive"], var.alarm_config_path) ? "${path.module}/templates/lambda/${var.alarm_config_path}.json" : var.alarm_config_path

  alarm_config = jsondecode(file(local.config_path))

  # Backward compatibility: merge lambda_functions into monitored_resources
  resources = merge(var.monitored_resources, var.lambda_functions)

  alarms = merge([
    for resource_key, alarm_configs in local.alarm_config : {
      for alarm in alarm_configs :
      "${resource_key}_${alarm.alarm_suffix}" => {
        resource_identifier = local.resources[resource_key]
        metric_name         = alarm.metric_name
        statistic           = alarm.statistic
        threshold           = var.alarm_thresholds[resource_key][alarm.alarm_suffix]
        comparison_operator = alarm.comparison_operator
        alarm_name          = "${var.resource_prefix}-${replace(resource_key, "_", "-")}-${alarm.alarm_suffix}"
        description         = alarm.description
        evaluation_periods  = var.alarm_evaluation_periods[resource_key][alarm.alarm_suffix]
        period              = var.alarm_periods[resource_key][alarm.alarm_suffix]
        actions_enabled     = alarm.severity == "warning" ? var.enable_warning_alarms : true
        namespace           = lookup(alarm, "namespace", "AWS/Lambda")
        dimensions          = lookup(alarm, "dimensions", {})
        dimension_name      = lookup(alarm, "dimension_name", "FunctionName")
      }
    }
  ]...)
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
