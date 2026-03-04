locals {
  appconfig_configuration_profile_id = try(tolist(data.aws_appconfig_configuration_profiles.appconfig_configuration_profiles.configuration_profile_ids)[0], null)
  appconfig_environment_id           = try(tolist(data.aws_appconfig_environments.appconfig_environments.environment_ids)[0], null)

  dms_simple_metric_alarm_configs = {
    source_latency_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencySource-High"
      metric_name         = "CDCLatencySource"
      threshold           = var.alarm_threshold_cdc_critical
      alarm_description   = "Critical - CDC latency on DMS source > ${var.alarm_threshold_cdc_critical} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      period              = var.alarm_period_cdc
    }
    target_latency_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencyTarget-High"
      metric_name         = "CDCLatencyTarget"
      threshold           = var.alarm_threshold_cdc_critical
      alarm_description   = "Critical - CDC latency on DMS target > ${var.alarm_threshold_cdc_critical} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      period              = var.alarm_period_cdc
    }
    source_latency_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencySource-Warning"
      metric_name         = "CDCLatencySource"
      threshold           = var.alarm_threshold_cdc_warning
      alarm_description   = "Warning - CDC latency on DMS source > ${var.alarm_threshold_cdc_warning} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      period              = var.alarm_period_cdc
    }
    target_latency_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencyTarget-Warning"
      metric_name         = "CDCLatencyTarget"
      threshold           = var.alarm_threshold_cdc_warning
      alarm_description   = "Warning - CDC latency on DMS target > ${var.alarm_threshold_cdc_warning} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      period              = var.alarm_period_cdc
    }
  }

  dms_metric_query_alarm_configs = {
    cdc_changes_disk_source_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesDiskSource-High"
      alarm_description   = "Critical - anomaly upper bound is >50% above CDCChangesDiskSource average"
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      datapoints_to_alarm = var.alarm_datapoints_cdc
      period              = var.alarm_period_cdc
      threshold           = 0 # Trigger when UPPER(ad1) - (m1 * 1.5) > 0

      metric_queries = [
        {
          id          = "m1"
          return_data = false

          metric = {
            metric_name = "CDCChangesDiskSource"
            namespace   = "AWS/DMS"
            period      = var.alarm_period_cdc
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = data.aws_dms_replication_task.dms_cdc_replication_task.id
            }
          }
        },
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          label       = "AnomalyDetectionBand"
          return_data = false
        },
        # Returns the amount by which the anomaly upper bound exceeds 1.5x the metric average
        {
          id          = "ad2"
          expression  = "UPPER(ad1) - (m1 * 1.5)"
          return_data = true
        }
      ]
    }
    cdc_changes_disk_source_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesDiskSource-Warning"
      alarm_description   = "Warning - anomaly upper bound is >30% above CDCChangesDiskSource average"
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      datapoints_to_alarm = var.alarm_datapoints_cdc
      period              = var.alarm_period_cdc
      threshold           = 0 # Trigger when UPPER(ad1) - (m1 * 1.3) > 0

      metric_queries = [
        # Base metric
        {
          id          = "m1"
          return_data = false

          metric = {
            metric_name = "CDCChangesDiskSource"
            namespace   = "AWS/DMS"
            period      = var.alarm_period_cdc
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = data.aws_dms_replication_task.dms_cdc_replication_task.id
            }
          }
        },
        # Anomaly detection band returns upper and lower bounds;
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          return_data = false
        },
        # Returns the amount by which the anomaly upper bound exceeds 1.3x the metric average
        {
          id          = "ad2"
          expression  = "UPPER(ad1) - (m1 * 1.3)"
          return_data = true
        }
      ]
    }
    cdc_changes_memory_source_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesMemorySource-High"
      alarm_description   = "Critical - anomaly upper bound is >50% above CDCChangesMemorySource average"
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      datapoints_to_alarm = var.alarm_datapoints_cdc
      period              = var.alarm_period_cdc
      threshold           = 0

      metric_queries = [
        {
          id          = "m1"
          return_data = false

          metric = {
            metric_name = "CDCChangesMemorySource"
            namespace   = "AWS/DMS"
            period      = var.alarm_period_cdc
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = data.aws_dms_replication_task.dms_cdc_replication_task.id
            }
          }
        },
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          label       = "AnomalyDetectionBand"
          return_data = false
        },
        # Returns the amount by which the anomaly upper bound exceeds 1.5x the metric average
        {
          id          = "ad2"
          expression  = "UPPER(ad1) - (m1 * 1.5)"
          return_data = true
        }
      ]
    }
    cdc_changes_memory_source_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesMemorySource-Warning"
      alarm_description   = "Warning - anomaly upper bound is >30% above CDCChangesMemorySource average"
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      datapoints_to_alarm = var.alarm_datapoints_cdc
      period              = var.alarm_period_cdc
      threshold           = 0 # Trigger when UPPER(ad1) - (m1 * 1.3) > 0

      metric_queries = [
        # Base metric
        {
          id          = "m1"
          return_data = false

          metric = {
            metric_name = "CDCChangesMemorySource"
            namespace   = "AWS/DMS"
            period      = var.alarm_period_cdc
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = data.aws_dms_replication_task.dms_cdc_replication_task.id
            }
          }
        },
        # Anomaly detection band returns upper and lower bounds;
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          return_data = false
        },
        # Returns the amount by which the anomaly upper bound exceeds 1.3x the metric average
        {
          id          = "ad2"
          expression  = "UPPER(ad1) - (m1 * 1.3)"
          return_data = true
        }
      ]
    }
  }
}

check "dms_alarm_config_schema" {
  assert {
    condition = alltrue([
      for name, cfg in merge(local.dms_simple_metric_alarm_configs, local.dms_metric_query_alarm_configs) : (
        (
          length(try(cfg.metric_queries, [])) == 0 &&
          try(cfg.metric_name, null) != null &&
          try(cfg.threshold, null) != null &&
          try(cfg.threshold_metric_id, null) == null
          ) || (
          length(try(cfg.metric_queries, [])) > 0 &&
          try(cfg.metric_name, null) == null &&
          (
            try(cfg.threshold_metric_id, null) != null ||
            try(cfg.threshold, null) != null
          )
        )
      )
    ])

    error_message = "Each DMS alarm config must be either: simple metric mode (metric_name + threshold, no metric_queries) OR metric query mode (metric_queries + threshold_metric_id/threshold, no metric_name)."
  }
}
check "dms_metric_query_single_return_data" {
  assert {
    condition = alltrue([
      for name, cfg in local.dms_metric_query_alarm_configs :
      length([
        for query in try(cfg.metric_queries, []) : query
        if try(query.return_data, false)
      ]) == 1
    ])

    error_message = "Each metric-query alarm in dms_metric_query_alarm_configs must set return_data = true on exactly one metric_query."
  }
}
