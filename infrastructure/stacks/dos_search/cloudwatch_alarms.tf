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
      duration_p95_warning           = var.search_lambda_duration_p95_warning_ms
      duration_p99_critical          = var.search_lambda_duration_p99_critical_ms
      concurrent_executions_warning  = var.search_lambda_concurrent_executions_warning
      concurrent_executions_critical = var.search_lambda_concurrent_executions_critical
      throttles_critical             = var.search_lambda_throttles_critical_threshold
      invocations_spike_critical     = var.search_lambda_invocations_baseline_per_hour * var.invocations_critical_spike_multiplier
      errors_warning                 = var.search_lambda_errors_warning_threshold
      errors_critical                = var.search_lambda_errors_critical_threshold
    }
    health_check_lambda = {
      errors_critical = var.health_check_errors_critical_threshold
    }
  }

  # Evaluation periods by severity
  alarm_evaluation_periods = {
    search_lambda = {
      duration_p95_warning           = var.lambda_alarm_evaluation_periods
      duration_p99_critical          = var.lambda_alarm_evaluation_periods
      concurrent_executions_warning  = var.lambda_alarm_evaluation_periods
      concurrent_executions_critical = var.lambda_alarm_evaluation_periods
      throttles_critical             = var.lambda_throttles_critical_evaluation_periods
      invocations_spike_critical     = var.lambda_alarm_evaluation_periods
      errors_warning                 = var.lambda_alarm_evaluation_periods
      errors_critical                = var.lambda_alarm_evaluation_periods
    }
    health_check_lambda = {
      errors_critical = var.health_check_errors_critical_evaluation_periods
    }
  }

  # Period (seconds) by severity
  alarm_periods = {
    search_lambda = {
      duration_p95_warning           = var.lambda_alarm_period_seconds
      duration_p99_critical          = var.lambda_alarm_period_seconds
      concurrent_executions_warning  = var.lambda_alarm_period_seconds
      concurrent_executions_critical = var.lambda_alarm_period_seconds
      throttles_critical             = var.lambda_throttles_critical_period_seconds
      invocations_spike_critical     = 3600 # 1 hour for invocations
      errors_warning                 = var.lambda_alarm_period_seconds
      errors_critical                = var.lambda_alarm_period_seconds
    }
    health_check_lambda = {
      errors_critical = var.health_check_errors_critical_period_seconds
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
      }
    }
  ]...)
}

module "cloudwatch_alarms" {
  for_each = local.alarms
  source   = "../../modules/cloudwatch-alarm"

  alarm_name          = each.value.alarm_name
  comparison_operator = each.value.comparison_operator
  evaluation_periods  = each.value.evaluation_periods
  metric_name         = each.value.metric_name
  period              = each.value.period
  statistic           = each.value.statistic
  threshold           = each.value.threshold
  alarm_description   = each.value.description
  sns_topic_arn       = module.sns.topic_arn
  function_name       = each.value.function_name
  workspace_suffix    = local.workspace_suffix
  namespace           = "AWS/Lambda"
  treat_missing_data  = "notBreaching"
}
