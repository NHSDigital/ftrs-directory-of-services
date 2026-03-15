module "api_gateway_monitoring" {
  # count = local.is_primary_environment ? 1 : 0 TODO: Enable once testing is complete
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix

  sns_topic_name   = "${local.alarms_topic_name}-api-gateway"
  sns_display_name = "DoS Search Alarms API Gateway"
  kms_key_id       = data.aws_kms_key.sns_kms_key.arn

  alarm_config_path = "api-gateway/config"

  monitored_resources = {
    dos_search_api = aws_api_gateway_rest_api.api_gateway.name
  }

  resource_metadata = {
    dos_search_api = {
      api_path = "/Organization"
      service  = "DoS Search"
    }
  }

  alarm_thresholds = {
    dos_search_api = {
      "latency-p95-warning"              = var.api_gateway_latency_p95_warning_ms
      "latency-p99-critical"             = var.api_gateway_latency_p99_critical_ms
      "integration-latency-p95-warning"  = var.api_gateway_integration_latency_p95_warning_ms
      "integration-latency-p99-critical" = var.api_gateway_integration_latency_p99_critical_ms
      "tps-critical"                     = var.api_gateway_tps_critical_threshold
      "usage-volume-warning"             = var.api_gateway_usage_volume_baseline * var.api_gateway_usage_volume_warning_multiplier
      "usage-volume-critical"            = var.api_gateway_usage_volume_baseline * var.api_gateway_usage_volume_critical_multiplier
      "4xx-errors-warning"               = var.api_gateway_4xx_errors_warning_threshold
      "4xx-errors-critical"              = var.api_gateway_4xx_errors_critical_threshold
      "5xx-errors-critical"              = var.api_gateway_5xx_errors_critical_threshold
      "status-endpoint-5xx-critical"     = var.api_gateway_status_endpoint_5xx_critical_threshold
    }
  }

  alarm_evaluation_periods = {
    dos_search_api = {
      "latency-p95-warning"              = var.api_gateway_alarm_evaluation_periods
      "latency-p99-critical"             = var.api_gateway_alarm_evaluation_periods
      "integration-latency-p95-warning"  = var.api_gateway_alarm_evaluation_periods
      "integration-latency-p99-critical" = var.api_gateway_alarm_evaluation_periods
      "tps-critical"                     = var.api_gateway_tps_evaluation_periods
      "usage-volume-warning"             = var.api_gateway_usage_volume_evaluation_periods
      "usage-volume-critical"            = var.api_gateway_usage_volume_evaluation_periods
      "4xx-errors-warning"               = var.api_gateway_4xx_errors_evaluation_periods
      "4xx-errors-critical"              = var.api_gateway_4xx_errors_evaluation_periods
      "5xx-errors-critical"              = var.api_gateway_5xx_errors_evaluation_periods
      "status-endpoint-5xx-critical"     = var.api_gateway_status_endpoint_5xx_evaluation_periods
    }
  }

  alarm_periods = {
    dos_search_api = {
      "latency-p95-warning"              = var.api_gateway_alarm_period_seconds
      "latency-p99-critical"             = var.api_gateway_alarm_period_seconds
      "integration-latency-p95-warning"  = var.api_gateway_alarm_period_seconds
      "integration-latency-p99-critical" = var.api_gateway_alarm_period_seconds
      "tps-critical"                     = var.api_gateway_tps_period_seconds
      "usage-volume-warning"             = var.api_gateway_usage_volume_period_seconds
      "usage-volume-critical"            = var.api_gateway_usage_volume_period_seconds
      "4xx-errors-warning"               = var.api_gateway_4xx_errors_period_seconds
      "4xx-errors-critical"              = var.api_gateway_4xx_errors_period_seconds
      "5xx-errors-critical"              = var.api_gateway_5xx_errors_period_seconds
      "status-endpoint-5xx-critical"     = var.api_gateway_status_endpoint_5xx_period_seconds
    }
  }

  api_gateway_log_group_name = aws_cloudwatch_log_group.api_gateway_log_group.name

  rate_limiting_429_critical_threshold          = var.api_gateway_429_critical_threshold
  rate_limiting_429_critical_period             = var.api_gateway_429_critical_period_seconds
  rate_limiting_429_critical_evaluation_periods = var.api_gateway_429_critical_evaluation_periods
  rate_limiting_429_warning_threshold           = var.api_gateway_429_warning_threshold
  rate_limiting_429_warning_period              = var.api_gateway_429_warning_period_seconds
  rate_limiting_429_warning_evaluation_periods  = var.api_gateway_429_warning_evaluation_periods

  enable_warning_alarms = var.enable_warning_alarms

  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  tags = {
    Name = local.alarms_topic_name
  }
}
