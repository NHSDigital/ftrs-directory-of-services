# =============================================================================
# ETL ODS Performance Monitoring (PERF-001, SEC-011)
# Dashboard + Alarms for: ods-daily-sync, ods-batch-transform, ods-sqs-batch-send
# Reference: requirements/nfrs/performance/nfrs.yaml (perf-etl-ods-latency control)
# =============================================================================

locals {
  extractor_function_name   = "${local.resource_prefix}-${var.extractor_name}${local.workspace_suffix}"
  transformer_function_name = "${local.resource_prefix}-${var.transformer_name}${local.workspace_suffix}"
  consumer_function_name    = "${local.resource_prefix}-${var.consumer_name}${local.workspace_suffix}"

  # PERF-001 thresholds from requirements/nfrs/performance/nfrs.yaml
  perf_thresholds = {
    ods_daily_sync = {
      p50_ms = 500
      p95_ms = 1500
      max_ms = 3000
    }
    ods_batch_transform = {
      p50_ms = 200
      p95_ms = 600
      max_ms = 1200
    }
    ods_sqs_batch_send = {
      p50_ms = 30
      p95_ms = 80
      max_ms = 200
    }
  }
}

# -----------------------------------------------------------------------------
# CloudWatch Dashboard
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_dashboard" "etl_ods_performance" {
  dashboard_name = "${local.resource_prefix}-performance${local.workspace_suffix}"

  dashboard_body = jsonencode({
    widgets = [
      # Row 1: Lambda Duration Overview with threshold annotations
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 8
        height = 6
        properties = {
          title   = "Extractor Duration (ods-daily-sync)"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", local.extractor_function_name, { stat = "p50", label = "p50" }],
            ["...", { stat = "p95", label = "p95" }],
            ["...", { stat = "Maximum", label = "max" }]
          ]
          annotations = {
            horizontal = [
              { value = local.perf_thresholds.ods_daily_sync.p95_ms, label = "p95 threshold (${local.perf_thresholds.ods_daily_sync.p95_ms}ms)", color = "#ff7f0e" },
              { value = local.perf_thresholds.ods_daily_sync.max_ms, label = "max threshold (${local.perf_thresholds.ods_daily_sync.max_ms}ms)", color = "#d62728" }
            ]
          }
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 0
        width  = 8
        height = 6
        properties = {
          title   = "Transformer Duration (ods-batch-transform)"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", local.transformer_function_name, { stat = "p50", label = "p50" }],
            ["...", { stat = "p95", label = "p95" }],
            ["...", { stat = "Maximum", label = "max" }]
          ]
          annotations = {
            horizontal = [
              { value = local.perf_thresholds.ods_batch_transform.p95_ms, label = "p95 threshold (${local.perf_thresholds.ods_batch_transform.p95_ms}ms)", color = "#ff7f0e" },
              { value = local.perf_thresholds.ods_batch_transform.max_ms, label = "max threshold (${local.perf_thresholds.ods_batch_transform.max_ms}ms)", color = "#d62728" }
            ]
          }
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 0
        width  = 8
        height = 6
        properties = {
          title   = "Consumer Duration (ods-sqs-batch-send)"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", local.consumer_function_name, { stat = "p50", label = "p50" }],
            ["...", { stat = "p95", label = "p95" }],
            ["...", { stat = "Maximum", label = "max" }]
          ]
          annotations = {
            horizontal = [
              { value = local.perf_thresholds.ods_sqs_batch_send.p95_ms, label = "p95 threshold (${local.perf_thresholds.ods_sqs_batch_send.p95_ms}ms)", color = "#ff7f0e" },
              { value = local.perf_thresholds.ods_sqs_batch_send.max_ms, label = "max threshold (${local.perf_thresholds.ods_sqs_batch_send.max_ms}ms)", color = "#d62728" }
            ]
          }
          period = 300
        }
      },
      # Row 2: Invocations and Errors
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "ETL Lambda Invocations"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = true
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", local.extractor_function_name, { label = "Extractor" }],
            ["...", local.transformer_function_name, { label = "Transformer" }],
            ["...", local.consumer_function_name, { label = "Consumer" }]
          ]
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "ETL Lambda Errors"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/Lambda", "Errors", "FunctionName", local.extractor_function_name, { label = "Extractor", color = "#d62728" }],
            ["...", local.transformer_function_name, { label = "Transformer", color = "#ff7f0e" }],
            ["...", local.consumer_function_name, { label = "Consumer", color = "#9467bd" }]
          ]
          period = 300
        }
      },
      # Row 3: SQS Queue Metrics
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6
        properties = {
          title   = "SQS Queue Depth"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", "${local.resource_prefix}-transform-queue${local.workspace_suffix}", { label = "Transform Queue" }],
            ["...", "${local.resource_prefix}-load-queue${local.workspace_suffix}", { label = "Load Queue" }]
          ]
          period = 60
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 12
        width  = 12
        height = 6
        properties = {
          title   = "DLQ Messages (Failures)"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", "${local.resource_prefix}-transform-dlq${local.workspace_suffix}", { label = "Transform DLQ", color = "#d62728" }],
            ["...", "${local.resource_prefix}-load-dlq${local.workspace_suffix}", { label = "Load DLQ", color = "#ff7f0e" }]
          ]
          period = 60
        }
      },
      # Row 4: Concurrent Executions and Throttles
      {
        type   = "metric"
        x      = 0
        y      = 18
        width  = 12
        height = 6
        properties = {
          title   = "Concurrent Executions"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/Lambda", "ConcurrentExecutions", "FunctionName", local.extractor_function_name, { label = "Extractor" }],
            ["...", local.transformer_function_name, { label = "Transformer" }],
            ["...", local.consumer_function_name, { label = "Consumer" }]
          ]
          period = 60
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 18
        width  = 12
        height = 6
        properties = {
          title   = "Throttles"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/Lambda", "Throttles", "FunctionName", local.extractor_function_name, { label = "Extractor", color = "#d62728" }],
            ["...", local.transformer_function_name, { label = "Transformer", color = "#ff7f0e" }],
            ["...", local.consumer_function_name, { label = "Consumer", color = "#9467bd" }]
          ]
          period = 60
        }
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# CloudWatch Alarms for P95 Latency Breaches (PERF-001)
# Evaluation: 3 consecutive 5-minute periods exceeding threshold
# -----------------------------------------------------------------------------

# Extractor Lambda (ods-daily-sync) P95 Latency Alarm
resource "aws_cloudwatch_metric_alarm" "extractor_p95_latency" {
  alarm_name          = "${local.resource_prefix}-extractor-p95-latency${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  extended_statistic  = "p95"
  threshold           = local.perf_thresholds.ods_daily_sync.p95_ms
  alarm_description   = "PERF-001: ods-daily-sync P95 latency exceeds ${local.perf_thresholds.ods_daily_sync.p95_ms}ms threshold. Control: perf-etl-ods-latency"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = local.extractor_function_name
  }

  tags = {
    NFR       = "PERF-001"
    Operation = "ods-daily-sync"
    ControlId = "perf-etl-ods-latency"
  }
}

# Transformer Lambda (ods-batch-transform) P95 Latency Alarm
resource "aws_cloudwatch_metric_alarm" "transformer_p95_latency" {
  alarm_name          = "${local.resource_prefix}-transformer-p95-latency${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  extended_statistic  = "p95"
  threshold           = local.perf_thresholds.ods_batch_transform.p95_ms
  alarm_description   = "PERF-001: ods-batch-transform P95 latency exceeds ${local.perf_thresholds.ods_batch_transform.p95_ms}ms threshold. Control: perf-etl-ods-latency"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = local.transformer_function_name
  }

  tags = {
    NFR       = "PERF-001"
    Operation = "ods-batch-transform"
    ControlId = "perf-etl-ods-latency"
  }
}

# Consumer Lambda (ods-sqs-batch-send) P95 Latency Alarm
resource "aws_cloudwatch_metric_alarm" "consumer_p95_latency" {
  alarm_name          = "${local.resource_prefix}-consumer-p95-latency${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  extended_statistic  = "p95"
  threshold           = local.perf_thresholds.ods_sqs_batch_send.p95_ms
  alarm_description   = "PERF-001: ods-sqs-batch-send P95 latency exceeds ${local.perf_thresholds.ods_sqs_batch_send.p95_ms}ms threshold. Control: perf-etl-ods-latency"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = local.consumer_function_name
  }

  tags = {
    NFR       = "PERF-001"
    Operation = "ods-sqs-batch-send"
    ControlId = "perf-etl-ods-latency"
  }
}

# -----------------------------------------------------------------------------
# Maximum Duration Alarms (Batch Window Protection)
# Single evaluation period - immediate alert on absolute max breach
# -----------------------------------------------------------------------------

# Extractor Lambda Maximum Duration Alarm
resource "aws_cloudwatch_metric_alarm" "extractor_max_duration" {
  alarm_name          = "${local.resource_prefix}-extractor-max-duration${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Maximum"
  threshold           = local.perf_thresholds.ods_daily_sync.max_ms
  alarm_description   = "PERF-001: ods-daily-sync exceeds absolute max ${local.perf_thresholds.ods_daily_sync.max_ms}ms. Control: perf-etl-ods-latency"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = local.extractor_function_name
  }

  tags = {
    NFR       = "PERF-001"
    Operation = "ods-daily-sync"
    ControlId = "perf-etl-ods-latency"
  }
}

# Transformer Lambda Maximum Duration Alarm
resource "aws_cloudwatch_metric_alarm" "transformer_max_duration" {
  alarm_name          = "${local.resource_prefix}-transformer-max-duration${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Maximum"
  threshold           = local.perf_thresholds.ods_batch_transform.max_ms
  alarm_description   = "PERF-001: ods-batch-transform exceeds absolute max ${local.perf_thresholds.ods_batch_transform.max_ms}ms. Control: perf-etl-ods-latency"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = local.transformer_function_name
  }

  tags = {
    NFR       = "PERF-001"
    Operation = "ods-batch-transform"
    ControlId = "perf-etl-ods-latency"
  }
}

# Consumer Lambda Maximum Duration Alarm
resource "aws_cloudwatch_metric_alarm" "consumer_max_duration" {
  alarm_name          = "${local.resource_prefix}-consumer-max-duration${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Maximum"
  threshold           = local.perf_thresholds.ods_sqs_batch_send.max_ms
  alarm_description   = "PERF-001: ods-sqs-batch-send exceeds absolute max ${local.perf_thresholds.ods_sqs_batch_send.max_ms}ms. Control: perf-etl-ods-latency"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = local.consumer_function_name
  }

  tags = {
    NFR       = "PERF-001"
    Operation = "ods-sqs-batch-send"
    ControlId = "perf-etl-ods-latency"
  }
}

# -----------------------------------------------------------------------------
# DLQ Message Count Alarm (Reliability Indicator)
# -----------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "transform_dlq_messages" {
  alarm_name          = "${local.resource_prefix}-transform-dlq-messages${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Messages in transform DLQ indicate processing failures"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = "${local.resource_prefix}-transform-dlq${local.workspace_suffix}"
  }

  tags = {
    NFR       = "REL-016"
    ControlId = "perf-etl-ods-latency"
  }
}

resource "aws_cloudwatch_metric_alarm" "load_dlq_messages" {
  alarm_name          = "${local.resource_prefix}-load-dlq-messages${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Messages in load DLQ indicate processing failures"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = "${local.resource_prefix}-load-dlq${local.workspace_suffix}"
  }

  tags = {
    NFR       = "REL-016"
    ControlId = "perf-etl-ods-latency"
  }
}
