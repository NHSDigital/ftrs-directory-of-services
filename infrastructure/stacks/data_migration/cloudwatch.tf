resource "aws_cloudwatch_log_data_protection_policy" "dms_db_protection_policy" {
  count = local.is_primary_environment ? 1 : 0

  log_group_name = module.dms_db_lambda[0].lambda_cloudwatch_log_group_name

  policy_document = jsonencode({
    Name    = "DmsDbLogDataProtectionPolicy"
    Version = "2021-06-01"
    Configuration = {
      CustomDataIdentifier = [
        { "Name" : "DMSUserPassword", "Regex" : "(?i)password\\s*[:=]\\s*['\"](.*?)['\"]" }
      ]
    }
    Statement = [
      {
        Sid = "Audit"
        DataIdentifier = [
          "DMSUserPassword"
        ]
        Operation = {
          Audit = {
            FindingsDestination = {
              CloudWatchLogs = {
                LogGroup = aws_cloudwatch_log_group.dms_db_data_protection_audit_log_group[0].name
              }
            }
          }
        }
      },
      {
        Sid = "Redact"
        DataIdentifier = [
          "DMSUserPassword"
        ]
        Operation = {
          Deidentify = {
            MaskConfig = {}
          }
        }
      }
    ]
  })
}

# Create CloudWatch log group for audit logs
resource "aws_cloudwatch_log_group" "dms_db_data_protection_audit_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  # checkov:skip=CKV_AWS_338: Justification: Non-production do not require long term log retention.
  count = local.is_primary_environment ? 1 : 0

  name              = "/aws/data-protection-audit/${var.environment}/${local.resource_prefix}-${var.dms_db_lambda_name}"
  retention_in_days = var.dms_audit_cloudwatch_logs_retention_days
}

module "dms_instance_monitoring" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix # Used for naming SNS topic and alarms

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "DMS Alarms"
  kms_key_id       = data.aws_kms_key.sns_kms_alias.arn

  alarm_config_path = "dms/instance/config"

  monitored_resources = {
    replication_instance = local.dms_replication_instance_id
  }

  resource_metadata = {
    replication_instance = {
      api_path = "N/A"
      service  = "DMS"
    }
  }

  alarm_descriptions = {
    replication_instance = {
      "cpu_critical"                = "Critical - CPU utilization > ${var.alarm_threshold_cpu_critical} percent"
      "cpu_warning"                 = "Warning - CPU utilization > ${var.alarm_threshold_cpu_warning} percent"
      "freeable_memory_warning"     = "Warning - Freeable memory < ${var.alarm_threshold_freeable_memory_warning} bytes"
      "freeable_memory_critical"    = "Critical - Freeable memory < ${var.alarm_threshold_freeable_memory_critical} bytes"
      "available_memory_warning"    = "Warning - Available memory < ${var.alarm_threshold_available_memory_warning} bytes"
      "available_memory_critical"   = "Critical - Available memory < ${var.alarm_threshold_available_memory_critical} bytes"
      "free_storage_space_warning"  = "Warning - Free storage space < ${var.alarm_threshold_free_storage_warning} bytes"
      "free_storage_space_critical" = "Critical - Free storage space < ${var.alarm_threshold_free_storage_critical} bytes"
      "swap_usage_warning"          = "Warning - Swap usage > ${var.alarm_threshold_swap_usage_warning} bytes"
      "swap_usage_critical"         = "Critical - Swap usage > ${var.alarm_threshold_swap_usage_critical} bytes"
      "write_latency_warning"       = "Warning - Write latency > ${var.alarm_threshold_write_latency_warning} milliseconds"
      "write_latency_critical"      = "Critical - Write latency > ${var.alarm_threshold_write_latency_critical} milliseconds"
      "read_latency_warning"        = "Warning - Read latency > ${var.alarm_threshold_read_latency_warning} milliseconds"
      "read_latency_critical"       = "Critical - Read latency > ${var.alarm_threshold_read_latency_critical} milliseconds"
      "read_iops_warning"           = "Warning - Read IOPS > ${var.alarm_threshold_read_iops_warning} ops per second"
      "read_iops_critical"          = "Critical - Read IOPS > ${var.alarm_threshold_read_iops_critical} ops per second"
      "read_throughput_warning"     = "Warning - Read throughput > ${var.alarm_threshold_read_throughput_warning} bytes per second"
      "read_throughput_critical"    = "Critical - Read throughput > ${var.alarm_threshold_read_throughput_critical} bytes per second"
      "write_throughput_warning"    = "Warning - Write throughput > ${var.alarm_threshold_write_throughput_warning} bytes per second"
      "write_throughput_critical"   = "Critical - Write throughput > ${var.alarm_threshold_write_throughput_critical} bytes per second"

      "network_receive_throughput_warning"   = "Warning- NetworkReceiveThroughput > 60% of replication instance network bandwidth"
      "network_receive_throughput_critical"  = "Critical - NetworkReceiveThroughput > 80% of replication instance network bandwidth"
      "network_transmit_throughput_warning"  = "Warning - NetworkTransmitThroughput > 60% of replication instance network bandwidth"
      "network_transmit_throughput_critical" = "Critical - NetworkTransmitThroughput > 80% of replication instance network bandwidth"

    }
  }

  alarm_thresholds = {
    replication_instance = {
      "cpu_critical"                = var.alarm_threshold_cpu_critical
      "cpu_warning"                 = var.alarm_threshold_cpu_warning
      "freeable_memory_warning"     = var.alarm_threshold_freeable_memory_warning
      "freeable_memory_critical"    = var.alarm_threshold_freeable_memory_critical
      "available_memory_warning"    = var.alarm_threshold_available_memory_warning
      "available_memory_critical"   = var.alarm_threshold_available_memory_critical
      "free_storage_space_warning"  = var.alarm_threshold_free_storage_warning
      "free_storage_space_critical" = var.alarm_threshold_free_storage_critical
      "swap_usage_warning"          = var.alarm_threshold_swap_usage_warning
      "swap_usage_critical"         = var.alarm_threshold_swap_usage_critical
      "write_latency_warning"       = var.alarm_threshold_write_latency_warning
      "write_latency_critical"      = var.alarm_threshold_write_latency_critical
      "read_latency_warning"        = var.alarm_threshold_read_latency_warning
      "read_latency_critical"       = var.alarm_threshold_read_latency_critical
      "read_iops_warning"           = var.alarm_threshold_read_iops_warning
      "read_iops_critical"          = var.alarm_threshold_read_iops_critical
      "read_throughput_warning"     = var.alarm_threshold_read_throughput_warning
      "read_throughput_critical"    = var.alarm_threshold_read_throughput_critical
      "write_throughput_warning"    = var.alarm_threshold_write_throughput_warning
      "write_throughput_critical"   = var.alarm_threshold_write_throughput_critical

      "network_receive_throughput_warning"   = local.dms_network_threshold_60pct
      "network_receive_throughput_critical"  = local.dms_network_threshold_80pct
      "network_transmit_throughput_warning"  = local.dms_network_threshold_60pct
      "network_transmit_throughput_critical" = local.dms_network_threshold_80pct

    }
  }

  alarm_evaluation_periods = {
    replication_instance = {
      "cpu_critical"                         = var.alarm_evaluation_periods
      "cpu_warning"                          = var.alarm_evaluation_periods
      "freeable_memory_warning"              = var.alarm_evaluation_periods
      "freeable_memory_critical"             = var.alarm_evaluation_periods
      "available_memory_warning"             = var.alarm_evaluation_periods
      "available_memory_critical"            = var.alarm_evaluation_periods
      "free_storage_space_warning"           = var.alarm_evaluation_periods
      "free_storage_space_critical"          = var.alarm_evaluation_periods
      "swap_usage_warning"                   = var.alarm_evaluation_periods
      "swap_usage_critical"                  = var.alarm_evaluation_periods
      "write_latency_warning"                = var.alarm_evaluation_periods
      "write_latency_critical"               = var.alarm_evaluation_periods
      "read_latency_warning"                 = var.alarm_evaluation_periods
      "read_latency_critical"                = var.alarm_evaluation_periods
      "read_iops_warning"                    = var.alarm_evaluation_periods
      "read_iops_critical"                   = var.alarm_evaluation_periods
      "read_throughput_warning"              = var.alarm_evaluation_periods
      "read_throughput_critical"             = var.alarm_evaluation_periods
      "write_throughput_warning"             = var.alarm_evaluation_periods
      "write_throughput_critical"            = var.alarm_evaluation_periods
      "network_receive_throughput_warning"   = var.alarm_evaluation_periods
      "network_receive_throughput_critical"  = var.alarm_evaluation_periods
      "network_transmit_throughput_warning"  = var.alarm_evaluation_periods
      "network_transmit_throughput_critical" = var.alarm_evaluation_periods
    }

  }

  alarm_periods = {
    replication_instance = {
      "cpu_warning"                          = var.alarm_period
      "cpu_critical"                         = var.alarm_period
      "freeable_memory_warning"              = var.alarm_period
      "freeable_memory_critical"             = var.alarm_period
      "available_memory_warning"             = var.alarm_period
      "available_memory_critical"            = var.alarm_period
      "free_storage_space_warning"           = var.alarm_period
      "free_storage_space_critical"          = var.alarm_period
      "swap_usage_warning"                   = var.alarm_period
      "swap_usage_critical"                  = var.alarm_period
      "write_latency_warning"                = var.alarm_period
      "write_latency_critical"               = var.alarm_period
      "read_latency_warning"                 = var.alarm_period
      "read_latency_critical"                = var.alarm_period
      "read_iops_warning"                    = var.alarm_period
      "read_iops_critical"                   = var.alarm_period
      "read_throughput_warning"              = var.alarm_period
      "read_throughput_critical"             = var.alarm_period
      "write_throughput_warning"             = var.alarm_period
      "write_throughput_critical"            = var.alarm_period
      "network_receive_throughput_warning"   = var.alarm_period
      "network_receive_throughput_critical"  = var.alarm_period
      "network_transmit_throughput_warning"  = var.alarm_period
      "network_transmit_throughput_critical" = var.alarm_period
    }
  }

  # alarm_datapoints_to_alarm = {
  #   replication_instance = {
  #     "instance_cpu_warning" = 1
  #   }
  # }

  enable_warning_alarms = var.enable_warning_alarms

  slack_notifier_enabled       = true
  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  tags = {
    Name = local.alarms_topic_name
  }
}

module "dms_task_monitoring" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix # Used for naming SNS topic and alarms

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "DMS Alarms"
  kms_key_id       = data.aws_kms_key.sns_kms_alias.arn

  alarm_config_path = "dms/task/config"

  monitored_resources = {
    replication_task = local.dms_cdc_replication_task_id
  }

  resource_metadata = {
    replication_task = {
      api_path = "N/A"
      service  = "DMS"
    }
  }

  alarm_descriptions = {
    replication_task = {
      "source_latency_critical" = "Critical - CDC latency on DMS source > ${var.alarm_threshold_cdc_critical} seconds"
      "target_latency_critical" = "Critical - CDC latency on DMS target > ${var.alarm_threshold_cdc_critical} seconds"
      "source_latency_warning"  = "Warning - CDC latency on DMS source > ${var.alarm_threshold_cdc_warning} seconds"
      "target_latency_warning"  = "Warning - CDC latency on DMS target > ${var.alarm_threshold_cdc_warning} seconds"
    }
  }

  alarm_thresholds = {
    replication_task = {
      "source_latency_critical" = var.alarm_threshold_cdc_critical
      "target_latency_critical" = var.alarm_threshold_cdc_critical
      "source_latency_warning"  = var.alarm_threshold_cdc_warning
      "target_latency_warning"  = var.alarm_threshold_cdc_warning
    }
  }

  alarm_evaluation_periods = {
    replication_task = {
      "source_latency_critical" = var.alarm_evaluation_periods
      "target_latency_critical" = var.alarm_evaluation_periods
      "source_latency_warning"  = var.alarm_evaluation_periods
      "target_latency_warning"  = var.alarm_evaluation_periods
    }
  }

  alarm_periods = {
    replication_task = {
      "source_latency_warning"  = var.alarm_period
      "source_latency_critical" = var.alarm_period
      "target_latency_warning"  = var.alarm_period
      "target_latency_critical" = var.alarm_period
    }
  }

  enable_warning_alarms = var.enable_warning_alarms

  slack_notifier_enabled       = true
  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  tags = {
    Name = local.alarms_topic_name
  }
}

    