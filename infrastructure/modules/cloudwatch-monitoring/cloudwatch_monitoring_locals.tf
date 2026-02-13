locals {
  # Support both template names and custom paths
  config_path = contains(["minimal", "standard", "comprehensive"], var.alarm_config_path) ? "${path.module}/templates/lambda/${var.alarm_config_path}.json" : var.alarm_config_path

  alarm_config = jsondecode(file(local.config_path))

  # Backward compatibility: merge lambda_functions into monitored_resources
  resources = merge(var.monitored_resources, var.lambda_functions)

  # Filter resources by template resource_type_filter if specified
  filtered_resources = var.resource_type_filter != null ? {
    for k, v in local.resources : k => v if contains(var.resource_type_filter, k)
  } : local.resources

  # Flatten alarm config: apply each template type to filtered resources
  alarms = merge([
    for template_key, alarm_configs in local.alarm_config : merge([
      for resource_key, resource_identifier in local.filtered_resources : {
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
