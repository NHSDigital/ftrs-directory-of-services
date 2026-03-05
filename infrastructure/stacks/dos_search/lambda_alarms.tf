module "lambda_monitoring" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix # Used for naming SNS topic and alarms

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "DoS Search Alarms"
  kms_key_id       = data.aws_kms_key.sns_kms_key.arn

  alarm_config_path = "lambda/config"

  monitored_resources = {
    search_lambda       = module.lambda.lambda_function_name
    health_check_lambda = module.health_check_lambda.lambda_function_name
  }

  resource_metadata = {
    search_lambda = {
      api_path = "/Organization"
      service  = "DoS Search"
    }
    health_check_lambda = {
      api_path = "/_status"
      service  = "DoS Search"
    }
  }

  alarm_thresholds = {
    search_lambda = {
      "duration-p95-warning"           = var.search_lambda_duration_p95_warning_ms
      "duration-p99-critical"          = var.search_lambda_duration_p99_critical_ms
      "concurrent-executions-warning"  = var.search_lambda_concurrent_executions_warning
      "concurrent-executions-critical" = var.search_lambda_concurrent_executions_critical
      "throttles-critical"             = var.search_lambda_throttles_critical_threshold
      "invocations-spike-critical"     = var.search_lambda_invocations_baseline_per_hour * var.invocations_critical_spike_multiplier
      "errors-warning"                 = var.search_lambda_errors_warning_threshold
      "errors-critical"                = var.search_lambda_errors_critical_threshold
    }
    health_check_lambda = {
      "errors-warning"  = var.health_check_errors_warning_threshold
      "errors-critical" = var.health_check_errors_critical_threshold
    }
  }

  alarm_evaluation_periods = {
    search_lambda = {
      "duration-p95-warning"           = var.lambda_alarm_evaluation_periods
      "duration-p99-critical"          = var.lambda_alarm_evaluation_periods
      "concurrent-executions-warning"  = var.lambda_alarm_evaluation_periods
      "concurrent-executions-critical" = var.lambda_alarm_evaluation_periods
      "throttles-critical"             = var.lambda_throttles_critical_evaluation_periods
      "invocations-spike-critical"     = var.lambda_alarm_evaluation_periods
      "errors-warning"                 = var.lambda_alarm_evaluation_periods
      "errors-critical"                = var.lambda_alarm_evaluation_periods
    }
    health_check_lambda = {
      "errors-warning"  = var.lambda_alarm_evaluation_periods
      "errors-critical" = var.health_check_errors_critical_evaluation_periods
    }
  }

  alarm_periods = {
    search_lambda = {
      "duration-p95-warning"           = var.lambda_alarm_period_seconds
      "duration-p99-critical"          = var.lambda_alarm_period_seconds
      "concurrent-executions-warning"  = var.lambda_alarm_period_seconds
      "concurrent-executions-critical" = var.lambda_alarm_period_seconds
      "throttles-critical"             = var.lambda_throttles_critical_period_seconds
      "invocations-spike-critical"     = var.invocations_spike_period_seconds
      "errors-warning"                 = var.lambda_alarm_period_seconds
      "errors-critical"                = var.lambda_alarm_period_seconds
    }
    health_check_lambda = {
      "errors-warning"  = var.lambda_alarm_period_seconds
      "errors-critical" = var.health_check_errors_critical_period_seconds
    }
  }

  enable_warning_alarms = var.enable_warning_alarms

  slack_notifier_enabled       = true
  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  tags = {
    Name = local.alarms_topic_name
  }
}
