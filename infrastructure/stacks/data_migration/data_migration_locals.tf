locals {
  appconfig_configuration_profile_id = try(tolist(data.aws_appconfig_configuration_profiles.appconfig_configuration_profiles.configuration_profile_ids)[0], null)
  appconfig_environment_id           = try(tolist(data.aws_appconfig_environments.appconfig_environments.environment_ids)[0], null)

  dms_alarm_configs = {
    source_latency_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencySource-High"
      metric_name         = "CDCLatencySource"
      threshold           = var.alarm_threshold_cdc_critical
      alarm_description   = "Critical - CDC latency on DMS source > ${var.alarm_threshold_cdc_critical} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      period              = var.alarm_period_cdc
      use_metric_query    = false
      metric_queries      = []
    }
    target_latency_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencyTarget-High"
      metric_name         = "CDCLatencyTarget"
      threshold           = var.alarm_threshold_cdc_critical
      alarm_description   = "Critical - CDC latency on DMS target > ${var.alarm_threshold_cdc_critical} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      period              = var.alarm_period_cdc
      use_metric_query    = false
      metric_queries      = []
    }
    source_latency_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencySource-Warning"
      metric_name         = "CDCLatencySource"
      threshold           = var.alarm_threshold_cdc_warning
      alarm_description   = "Warning - CDC latency on DMS source > ${var.alarm_threshold_cdc_warning} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      period              = var.alarm_period_cdc
      use_metric_query    = false
      metric_queries      = []
    }
    target_latency_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencyTarget-Warning"
      metric_name         = "CDCLatencyTarget"
      threshold           = var.alarm_threshold_cdc_warning
      alarm_description   = "Warning - CDC latency on DMS target > ${var.alarm_threshold_cdc_warning} seconds"
      datapoints_to_alarm = var.alarm_datapoints_cdc
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      period              = var.alarm_period_cdc
      use_metric_query    = false
      metric_queries      = []
    }
    cdc_changes_disk_source_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesDiskSource-High"
      alarm_description   = "Critical - CDCChangesDiskSource is >50% above baseline"
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      datapoints_to_alarm = var.alarm_datapoints_cdc
      period              = var.alarm_period_cdc

      threshold_metric_id = "ad1" # Use the ID of the anomaly detection metric query as the threshold 

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
          return_data = true
        },
        # 50% above the upper band returned by the anomaly detection above
        {
          id          = "ad2"
          expression  = "m1 - (UPPER(ad1)* 1.5)"
          return_data = true
        }
      ]
    }
    cdc_changes_disk_source_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesDiskSource-Warning"
      alarm_description   = "Warning - CDCChangesDiskSource is >30% above baseline"
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      datapoints_to_alarm = var.alarm_datapoints_cdc
      period              = var.alarm_period_cdc

      threshold_metric_id = "ad2" # Use the ID of the anomaly detection metric query as the threshold 

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
        # 30% above the upper band returned by the anomaly detection above
        {
          id          = "ad2"
          expression  = "m1 - (UPPER(ad1)* 1.3)"
          return_data = true
        }
      ]
    }
    cdc_changes_memory_source_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesMemorySource-High"
      alarm_description   = "Critical - CDCChangesMemorySource is >50% above baseline"
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      datapoints_to_alarm = var.alarm_datapoints_cdc
      period              = var.alarm_period_cdc

      threshold_metric_id = "ad1" # Use the ID of the anomaly detection metric query as the threshold 

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
          return_data = true
        },
        # 50% above the upper band returned by the anomaly detection above
        {
          id          = "ad2"
          expression  = "m1 - (UPPER(ad1)* 1.5)"
          return_data = true
        }
      ]
    }
    cdc_changes_memory_source_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesMemorySource-Warning"
      alarm_description   = "Warning - CDCChangesMemorySource is >30% above baseline"
      evaluation_periods  = var.alarm_evaluation_periods_cdc
      datapoints_to_alarm = var.alarm_datapoints_cdc
      period              = var.alarm_period_cdc

      threshold_metric_id = "ad2" # Use the ID of the anomaly detection metric query as the threshold 

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
        # 30% above the upper band returned by the anomaly detection above
        {
          id          = "ad2"
          expression  = "m1 - (UPPER(ad1)* 1.3)"
          return_data = true
        }
      ]
    }
  }
}