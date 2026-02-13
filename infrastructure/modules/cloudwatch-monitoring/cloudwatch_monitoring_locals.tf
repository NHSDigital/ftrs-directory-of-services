locals {
  config_path = "${path.module}/templates/${var.alarm_config_path}.json"

  alarm_config = jsondecode(file(local.config_path))

  resources = var.monitored_resources

  #Flatten alarm config: apply each template type to resources
  alarms = merge([
    for template_key, alarm_configs in local.alarm_config : merge([
      for resource_key, resource_identifier in local.resources : {
        for alarm in alarm_configs :
        "${resource_key}_${alarm.alarm_suffix}" => {
          resource_identifier = resource_identifier
          metric_name         = alarm.metric_name
          statistic           = alarm.statistic
          threshold           = lookup(lookup(var.alarm_thresholds, resource_key, {}), alarm.alarm_suffix, null)
          comparison_operator = alarm.comparison_operator
          alarm_name          = "${var.resource_prefix}-${replace(resource_key, "_", "-")}-${alarm.alarm_suffix}"
          description         = alarm.description
          evaluation_periods  = lookup(lookup(var.alarm_evaluation_periods, resource_key, {}), alarm.alarm_suffix, 1)
          period              = lookup(lookup(var.alarm_periods, resource_key, {}), alarm.alarm_suffix, 60)
          actions_enabled     = alarm.severity == "warning" ? var.enable_warning_alarms : true
          namespace           = lookup(alarm, "namespace", "AWS/Lambda")
          dimensions          = lookup(alarm, "dimensions", {})
          dimension_name      = lookup(alarm, "dimension_name", "FunctionName")
        }
        if lookup(lookup(var.alarm_thresholds, resource_key, {}), alarm.alarm_suffix, null) != null
      }
    ]...)
  ]...)
}
