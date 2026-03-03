locals {
  appconfig_configuration_profile_id = try(tolist(data.aws_appconfig_configuration_profiles.appconfig_configuration_profiles.configuration_profile_ids)[0], null)
  appconfig_environment_id           = try(tolist(data.aws_appconfig_environments.appconfig_environments.environment_ids)[0], null)

  dms_cdc_latency_alarm_configs = {
    source_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencySource-High"
      metric_name         = "CDCLatencySource"
      threshold           = var.alarm_threshold_cdc_critical
      alarm_description   = "Critical - CDC latency on DMS source > ${var.alarm_threshold_cdc_critical} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
    }
    target_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencyTarget-High"
      metric_name         = "CDCLatencyTarget"
      threshold           = var.alarm_threshold_cdc_critical
      alarm_description   = "Critical - CDC latency on DMS target > ${var.alarm_threshold_cdc_critical} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
    }
    source_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencySource-Warning"
      metric_name         = "CDCLatencySource"
      threshold           = var.alarm_threshold_cdc_warning
      alarm_description   = "Warning - CDC latency on DMS source > ${var.alarm_threshold_cdc_warning} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
    }
    target_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencyTarget-Warning"
      metric_name         = "CDCLatencyTarget"
      threshold           = var.alarm_threshold_cdc_warning
      alarm_description   = "Warning - CDC latency on DMS target > ${var.alarm_threshold_cdc_warning} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
    }
  }
}
