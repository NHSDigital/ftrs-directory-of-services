################################################################################
# CloudWatch Alarm Configuration
################################################################################

locals {
  alarm_config = jsondecode(file("${path.module}/alarms/lambda-config.json"))

  # Lambda function mapping
  lambda_functions = {
    search_lambda       = module.lambda.lambda_function_name
    health_check_lambda = module.health_check_lambda.lambda_function_name
  }

  # Threshold mapping by severity
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
      "errors-critical" = var.health_check_errors_critical_threshold
    }
  }

  # Evaluation periods by severity
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
      "errors-critical" = var.health_check_errors_critical_evaluation_periods
    }
  }

  # Period (seconds) by severity
  alarm_periods = {
    search_lambda = {
      "duration-p95-warning"           = var.lambda_alarm_period_seconds
      "duration-p99-critical"          = var.lambda_alarm_period_seconds
      "concurrent-executions-warning"  = var.lambda_alarm_period_seconds
      "concurrent-executions-critical" = var.lambda_alarm_period_seconds
      "throttles-critical"             = var.lambda_throttles_critical_period_seconds
      "invocations-spike-critical"     = 3600 # 1 hour for invocations
      "errors-warning"                 = var.lambda_alarm_period_seconds
      "errors-critical"                = var.lambda_alarm_period_seconds
    }
    health_check_lambda = {
      "errors-critical" = var.health_check_errors_critical_period_seconds
    }
  }

  # Generate alarms from JSON config
  alarms = merge([
    for lambda_type, alarm_configs in local.alarm_config : {
      for alarm in alarm_configs :
      "${lambda_type}_${alarm.alarm_suffix}" => {
        function_name       = local.lambda_functions[lambda_type]
        metric_name         = alarm.metric_name
        statistic           = alarm.statistic
        threshold           = local.alarm_thresholds[lambda_type][alarm.alarm_suffix]
        comparison_operator = alarm.comparison_operator
        alarm_name          = "${local.resource_prefix}-${replace(lambda_type, "_", "-")}-${alarm.alarm_suffix}"
        description         = alarm.description
        evaluation_periods  = local.alarm_evaluation_periods[lambda_type][alarm.alarm_suffix]
        period              = local.alarm_periods[lambda_type][alarm.alarm_suffix]
        actions_enabled     = alarm.severity == "warning" ? var.enable_warning_alarms : true
      }
    }
  ]...)
}
