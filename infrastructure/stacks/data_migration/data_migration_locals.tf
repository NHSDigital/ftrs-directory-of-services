locals {
  appconfig_configuration_profile_id = try(tolist(data.aws_appconfig_configuration_profiles.appconfig_configuration_profiles.configuration_profile_ids)[0], null)
  appconfig_environment_id           = try(tolist(data.aws_appconfig_environments.appconfig_environments.environment_ids)[0], null)

  # 
  # DMS replication instance class -> max network bandwidth (bytes/sec)
  # Fill values from your approved source of truth.
  dms_instance_bandwidth_bytes_per_sec = {
    "dms.t3.small" = 30000000 # TODO: 30 megabytes per second is a placeholder value, replace with actual bandwidth for dms.t3.small
  }

  dms_instance_bandwidth_bps = lookup(
    local.dms_instance_bandwidth_bytes_per_sec,
    var.dms_replication_instance_class,
    null
  )

  # 80% threshold for critical alarms
  dms_network_threshold_80pct = local.dms_instance_bandwidth_bps == null ? null : floor(local.dms_instance_bandwidth_bps * 0.8)
  # 60% threshold for warnings
  dms_network_threshold_60pct = local.dms_instance_bandwidth_bps == null ? null : floor(local.dms_instance_bandwidth_bps * 0.6)
  # 
  dms_simple_metric_alarm_configs = {
    source_latency_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencySource-High"
      metric_name         = "CDCLatencySource"
      threshold           = var.alarm_threshold_cdc_critical
      alarm_description   = "Critical - CDC latency on DMS source > ${var.alarm_threshold_cdc_critical} seconds"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
      }
    }
    target_latency_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencyTarget-High"
      metric_name         = "CDCLatencyTarget"
      threshold           = var.alarm_threshold_cdc_critical
      alarm_description   = "Critical - CDC latency on DMS target > ${var.alarm_threshold_cdc_critical} seconds"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
      }
    }
    source_latency_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencySource-Warning"
      metric_name         = "CDCLatencySource"
      threshold           = var.alarm_threshold_cdc_warning
      alarm_description   = "Warning - CDC latency on DMS source > ${var.alarm_threshold_cdc_warning} seconds"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
      }
    }
    target_latency_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCLatencyTarget-Warning"
      metric_name         = "CDCLatencyTarget"
      threshold           = var.alarm_threshold_cdc_warning
      alarm_description   = "Warning - CDC latency on DMS target > ${var.alarm_threshold_cdc_warning} seconds"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
      }
    }
    instance_cpu_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceCPU-Warning"
      metric_name         = "CPUUtilization"
      threshold           = var.alarm_threshold_cpu_warning
      alarm_description   = "Warning - CPU utilization > ${var.alarm_threshold_cpu_warning} percent"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_cpu_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceCPU-High"
      metric_name         = "CPUUtilization"
      threshold           = var.alarm_threshold_cpu_critical
      alarm_description   = "Critical - CPU utilization > ${var.alarm_threshold_cpu_critical} percent"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_freeable_memory_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceFreeableMemory-High"
      metric_name         = "FreeableMemory"
      comparison_operator = "LessThanThreshold"
      threshold           = var.alarm_threshold_freeable_memory_critical
      alarm_description   = "Critical - Freeable memory < ${var.alarm_threshold_freeable_memory_critical} bytes"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_freeable_memory_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceFreeableMemory-Warning"
      metric_name         = "FreeableMemory"
      comparison_operator = "LessThanThreshold"
      threshold           = var.alarm_threshold_freeable_memory_warning
      alarm_description   = "Warning - Freeable memory < ${var.alarm_threshold_freeable_memory_warning} bytes"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_available_memory_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceAvailableMemory-High"
      metric_name         = "AvailableMemory"
      comparison_operator = "LessThanThreshold"
      threshold           = var.alarm_threshold_available_memory_critical
      alarm_description   = "Critical - Available memory < ${var.alarm_threshold_available_memory_critical} bytes"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_available_memory_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceAvailableMemory-Warning"
      metric_name         = "AvailableMemory"
      comparison_operator = "LessThanThreshold"
      threshold           = var.alarm_threshold_available_memory_warning
      alarm_description   = "Warning - Available memory < ${var.alarm_threshold_available_memory_warning} bytes"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_free_storage_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceFreeStorage-High"
      metric_name         = "FreeStorageSpace"
      comparison_operator = "LessThanThreshold"
      threshold           = var.alarm_threshold_free_storage_critical
      alarm_description   = "Critical - Free storage space < ${var.alarm_threshold_free_storage_critical} bytes"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_free_storage_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceFreeStorage-Warning"
      metric_name         = "FreeStorageSpace"
      comparison_operator = "LessThanThreshold"
      threshold           = var.alarm_threshold_free_storage_warning
      alarm_description   = "Warning - Free storage space < ${var.alarm_threshold_free_storage_warning} bytes"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_swap_usage_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceSwapUsage-High"
      metric_name         = "SwapUsage"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_swap_usage_critical
      alarm_description   = "Critical - Swap usage > ${var.alarm_threshold_swap_usage_critical} bytes"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_swap_usage_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceSwapUsage-Warning"
      metric_name         = "SwapUsage"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_swap_usage_warning
      alarm_description   = "Warning - Swap usage > ${var.alarm_threshold_swap_usage_warning} bytes"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_write_latency_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceWriteLatency-High"
      metric_name         = "WriteLatency"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_write_latency_critical
      alarm_description   = "Critical - Write latency > ${var.alarm_threshold_write_latency_critical} ms"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_write_latency_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceWriteLatency-Warning"
      metric_name         = "WriteLatency"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_write_latency_warning
      alarm_description   = "Warning - Write latency > ${var.alarm_threshold_write_latency_warning} ms"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_read_latency_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceReadLatency-High"
      metric_name         = "ReadLatency"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_read_latency_critical
      alarm_description   = "Critical - Read latency > ${var.alarm_threshold_read_latency_critical} ms"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_read_latency_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceReadLatency-Warning"
      metric_name         = "ReadLatency"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_read_latency_warning
      alarm_description   = "Warning - Read latency > ${var.alarm_threshold_read_latency_warning} ms"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_read_iops_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceReadIOPS-High"
      metric_name         = "ReadIOPS"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_read_iops_critical
      alarm_description   = "Critical - Read IOPS > ${var.alarm_threshold_read_iops_critical} ops per second"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_read_iops_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceReadIOPS-Warning"
      metric_name         = "ReadIOPS"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_read_iops_warning
      alarm_description   = "Warning - Read IOPS > ${var.alarm_threshold_read_iops_warning} ops per second"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_read_throughput_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceReadThroughput-High"
      metric_name         = "ReadThroughput"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_read_throughput_critical
      alarm_description   = "Critical - Read Throughput > ${var.alarm_threshold_read_throughput_critical} bytes per second"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_read_throughput_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceReadThroughput-Warning"
      metric_name         = "ReadThroughput"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_read_throughput_warning
      alarm_description   = "Warning - Read Throughput > ${var.alarm_threshold_read_throughput_warning} bytes per second"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_write_throughput_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceWriteThroughput-High"
      metric_name         = "WriteThroughput"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_write_throughput_critical
      alarm_description   = "Critical - Write Throughput > ${var.alarm_threshold_write_throughput_critical} bytes per second"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    instance_write_throughput_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-InstanceWriteThroughput-Warning"
      metric_name         = "WriteThroughput"
      comparison_operator = "GreaterThanThreshold"
      threshold           = var.alarm_threshold_write_throughput_warning
      alarm_description   = "Warning - Write Throughput > ${var.alarm_threshold_write_throughput_warning} bytes per second"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    network_receive_throughput_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-NetworkReceiveThroughput-Critical"
      metric_name         = "NetworkReceiveThroughput"
      comparison_operator = "GreaterThanThreshold"
      threshold           = local.dms_network_threshold_80pct
      alarm_description   = "Critical - NetworkReceiveThroughput > 80% of replication instance network bandwidth"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    network_receive_throughput_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-NetworkReceiveThroughput-Warning"
      metric_name         = "NetworkReceiveThroughput"
      comparison_operator = "GreaterThanThreshold"
      threshold           = local.dms_network_threshold_60pct
      alarm_description   = "Warning - NetworkReceiveThroughput > 60% of replication instance network bandwidth"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    network_transmit_throughput_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-NetworkTransmitThroughput-Critical"
      metric_name         = "NetworkTransmitThroughput"
      comparison_operator = "GreaterThanThreshold"
      threshold           = local.dms_network_threshold_80pct
      alarm_description   = "Critical - NetworkTransmitThroughput > 80% of replication instance network bandwidth"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
    network_transmit_throughput_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-NetworkTransmitThroughput-Warning"
      metric_name         = "NetworkTransmitThroughput"
      comparison_operator = "GreaterThanThreshold"
      threshold           = local.dms_network_threshold_60pct
      alarm_description   = "Warning - NetworkTransmitThroughput > 60% of replication instance network bandwidth"
      datapoints_to_alarm = var.alarm_datapoints
      evaluation_periods  = var.alarm_evaluation_periods
      period              = var.alarm_period
      dimensions = {
        ReplicationInstanceIdentifier = aws_dms_replication_instance.dms_replication_instance[0].id
      }
    }
  }

  dms_metric_query_alarm_configs = {
    cdc_changes_disk_source_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesDiskSource-High"
      alarm_description   = "Critical - CDCChangesDiskSource exceeds anomaly detection upper band (ANOMALY_DETECTION_BAND m1,2)"
      evaluation_periods  = var.alarm_evaluation_periods
      datapoints_to_alarm = var.alarm_datapoints
      period              = var.alarm_period
      comparison_operator = "GreaterThanUpperThreshold"
      threshold_metric_id = "ad1" # Use the anomaly detection upper band as the threshold for the alarm

      metric_queries = [
        {
          id          = "m1"
          return_data = true

          metric = {
            metric_name = "CDCChangesDiskSource"
            namespace   = "AWS/DMS"
            period      = var.alarm_period
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
            }
          }
        },
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          label       = "AnomalyDetectionBand"
          return_data = true
        }
      ]
    }
    cdc_changes_disk_source_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesDiskSource-Warning"
      alarm_description   = "Warning - CDCChangesDiskSource exceeds anomaly detection upper band (ANOMALY_DETECTION_BAND m1,2)"
      evaluation_periods  = var.alarm_evaluation_periods
      datapoints_to_alarm = var.alarm_datapoints
      period              = var.alarm_period
      comparison_operator = "GreaterThanUpperThreshold"
      threshold_metric_id = "ad1" # Use the anomaly detection upper band as the threshold for the alarm

      metric_queries = [
        # Base metric
        {
          id          = "m1"
          return_data = true

          metric = {
            metric_name = "CDCChangesDiskSource"
            namespace   = "AWS/DMS"
            period      = var.alarm_period
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
            }
          }
        },
        # Anomaly detection band returns upper and lower bounds;
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          return_data = true
        }
      ]
    }
    cdc_changes_memory_source_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesMemorySource-High"
      alarm_description   = "Critical - CDCChangesMemorySource exceeds anomaly detection upper band (ANOMALY_DETECTION_BAND m1,2)"
      evaluation_periods  = var.alarm_evaluation_periods
      datapoints_to_alarm = var.alarm_datapoints
      period              = var.alarm_period
      comparison_operator = "GreaterThanUpperThreshold"
      threshold_metric_id = "ad1" # Use the anomaly detection upper band as the threshold for the alarm

      metric_queries = [
        {
          id          = "m1"
          return_data = true

          metric = {
            metric_name = "CDCChangesMemorySource"
            namespace   = "AWS/DMS"
            period      = var.alarm_period
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
            }
          }
        },
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          label       = "AnomalyDetectionBand"
          return_data = true
        }
      ]
    }
    cdc_changes_memory_source_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesMemorySource-Warning"
      alarm_description   = "Warning - CDCChangesMemorySource exceeds anomaly detection upper band (ANOMALY_DETECTION_BAND m1,2)"
      evaluation_periods  = var.alarm_evaluation_periods
      datapoints_to_alarm = var.alarm_datapoints
      period              = var.alarm_period
      comparison_operator = "GreaterThanUpperThreshold"
      threshold_metric_id = "ad1" # Use the anomaly detection upper band as the threshold for the alarm

      metric_queries = [
        # Base metric
        {
          id          = "m1"
          return_data = true

          metric = {
            metric_name = "CDCChangesMemorySource"
            namespace   = "AWS/DMS"
            period      = var.alarm_period
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
            }
          }
        },
        # Anomaly detection band returns upper and lower bounds;
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          return_data = true
        }
      ]
    }
    cdc_changes_disk_target_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesDiskTarget-High"
      alarm_description   = "Critical - CDCChangesDiskTarget exceeds anomaly detection upper band (ANOMALY_DETECTION_BAND m1,2)"
      evaluation_periods  = var.alarm_evaluation_periods
      datapoints_to_alarm = var.alarm_datapoints
      period              = var.alarm_period
      comparison_operator = "GreaterThanUpperThreshold"
      threshold_metric_id = "ad1" # Use the anomaly detection upper band as the threshold for the alarm

      metric_queries = [
        {
          id          = "m1"
          return_data = true

          metric = {
            metric_name = "CDCChangesDiskTarget"
            namespace   = "AWS/DMS"
            period      = var.alarm_period
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
            }
          }
        },
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          label       = "AnomalyDetectionBand"
          return_data = true
        }
      ]
    }
    cdc_changes_disk_target_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesDiskTarget-Warning"
      alarm_description   = "Warning - CDCChangesDiskTarget exceeds anomaly detection upper band (ANOMALY_DETECTION_BAND m1,2)"
      evaluation_periods  = var.alarm_evaluation_periods
      datapoints_to_alarm = var.alarm_datapoints
      period              = var.alarm_period
      comparison_operator = "GreaterThanUpperThreshold"
      threshold_metric_id = "ad1" # Use the anomaly detection upper band as the threshold for the alarm

      metric_queries = [
        # Base metric
        {
          id          = "m1"
          return_data = true

          metric = {
            metric_name = "CDCChangesDiskTarget"
            namespace   = "AWS/DMS"
            period      = var.alarm_period
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
            }
          }
        },
        # Anomaly detection band returns upper and lower bounds;
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          return_data = true
        }
      ]
    }
    cdc_changes_memory_target_critical = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesMemoryTarget-High"
      alarm_description   = "Critical - CDCChangesMemoryTarget exceeds anomaly detection upper band (ANOMALY_DETECTION_BAND m1,2)"
      evaluation_periods  = var.alarm_evaluation_periods
      datapoints_to_alarm = var.alarm_datapoints
      period              = var.alarm_period
      comparison_operator = "GreaterThanUpperThreshold"
      threshold_metric_id = "ad1" # Use the anomaly detection upper band as the threshold for the alarm

      metric_queries = [
        {
          id          = "m1"
          return_data = true

          metric = {
            metric_name = "CDCChangesMemoryTarget"
            namespace   = "AWS/DMS"
            period      = var.alarm_period
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
            }
          }
        },
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          label       = "AnomalyDetectionBand"
          return_data = true
        }
      ]
    }
    cdc_changes_memory_target_warning = {
      alarm_name          = "${local.resource_prefix}-DMS-CDCChangesMemoryTarget-Warning"
      alarm_description   = "Warning - CDCChangesMemoryTarget exceeds anomaly detection upper band (ANOMALY_DETECTION_BAND m1,2)"
      evaluation_periods  = var.alarm_evaluation_periods
      datapoints_to_alarm = var.alarm_datapoints
      period              = var.alarm_period
      comparison_operator = "GreaterThanUpperThreshold"
      threshold_metric_id = "ad1" # Use the anomaly detection upper band as the threshold for the alarm

      metric_queries = [
        # Base metric
        {
          id          = "m1"
          return_data = true

          metric = {
            metric_name = "CDCChangesMemoryTarget"
            namespace   = "AWS/DMS"
            period      = var.alarm_period
            stat        = "Average"

            dimensions = {
              ReplicationTaskIdentifier = aws_dms_replication_task.dms_cdc_replication_task[0].replication_task_id
            }
          }
        },
        # Anomaly detection band returns upper and lower bounds;
        {
          id          = "ad1"
          expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
          return_data = true
        }
      ]
    }
  }
}

# checks
check "dms_alarm_config_schema" {
  assert {
    condition = local.is_primary_environment ? alltrue([
      for name, cfg in merge(local.dms_simple_metric_alarm_configs, local.dms_metric_query_alarm_configs) : (
        (
          length(try(cfg.metric_queries, [])) == 0 &&
          try(cfg.metric_name, null) != null &&
          try(cfg.threshold, null) != null &&
          try(cfg.threshold_metric_id, null) == null &&
          try(cfg.dimensions, null) != null
          ) || (
          length(try(cfg.metric_queries, [])) > 0 &&
          try(cfg.metric_name, null) == null &&
          try(cfg.comparison_operator, null) != null &&
          (
            (
              try(cfg.threshold_metric_id, null) != null &&
              try(cfg.threshold, null) == null
              ) || (
              try(cfg.threshold, null) != null &&
              try(cfg.threshold_metric_id, null) == null
            )
          )
        )
      )
    ]) : true

    error_message = "Each DMS alarm config must be either: simple metric mode (metric_name + threshold + dimensions, no metric_queries/threshold_metric_id) OR metric query mode (metric_queries + comparison_operator + exactly one of threshold or threshold_metric_id, no metric_name)."
  }
}
check "dms_metric_query_single_return_data" {
  assert {
    condition = local.is_primary_environment ? alltrue([
      for name, cfg in local.dms_metric_query_alarm_configs : (
        try(cfg.threshold_metric_id, null) != null ? (
          length([
            for query in try(cfg.metric_queries, []) : query
            if try(query.id, null) == cfg.threshold_metric_id
          ]) == 1 &&
          length([
            for query in try(cfg.metric_queries, []) : query
            if try(query.id, null) == cfg.threshold_metric_id && try(query.return_data, false)
          ]) == 1
          ) : (
          length([
            for query in try(cfg.metric_queries, []) : query
            if try(query.return_data, false)
          ]) == 1
        )
      )
    ]) : true

    error_message = "Metric-query alarms must be valid: if threshold_metric_id is set, the matching query id must exist exactly once and have return_data = true; otherwise exactly one query must have return_data = true."
  }
}

check "dms_simple_alarm_dimensions_required" {
  assert {
    condition = local.is_primary_environment ? alltrue([
      for name, cfg in local.dms_simple_metric_alarm_configs :
      try(cfg.dimensions, null) != null && length(keys(cfg.dimensions)) > 0
    ]) : true

    error_message = "Each simple alarm in dms_simple_metric_alarm_configs must define a non-empty dimensions map."
  }
}

check "dms_replication_instance_class_supported" {
  assert {
    condition = local.is_primary_environment ? contains(
      keys(local.dms_instance_bandwidth_bytes_per_sec),
      var.dms_replication_instance_class
    ) : true
    error_message = "Unsupported dms_replication_instance_class for bandwidth lookup. Add it to local.dms_instance_bandwidth_bytes_per_sec."
  }
}

check "dms_replication_instance_bandwidth_configured" {
  assert {
    condition     = local.is_primary_environment ? (local.dms_instance_bandwidth_bps != null && local.dms_instance_bandwidth_bps > 0) : true
    error_message = "Bandwidth bytes/sec must be set (> 0) for the selected dms_replication_instance_class."
  }
}
