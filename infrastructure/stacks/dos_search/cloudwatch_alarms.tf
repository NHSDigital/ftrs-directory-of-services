################################################################################
# CloudWatch Alarm Thresholds
################################################################################

locals {
  alarm_config = jsondecode(file("${path.module}/alarms/lambda-config.json"))

  # Threshold mapping
  thresholds = {
    search_lambda = {
      Duration             = var.search_lambda_duration_threshold_ms
      ConcurrentExecutions = var.search_lambda_concurrent_executions_threshold
      Throttles            = var.search_lambda_throttles_threshold
      Invocations          = var.search_lambda_invocations_threshold
      Errors               = var.search_lambda_errors_threshold
    }
    health_check_lambda = {
      Duration             = var.health_check_lambda_duration_threshold_ms
      ConcurrentExecutions = var.health_check_lambda_concurrent_executions_threshold
      Throttles            = var.health_check_lambda_throttles_threshold
      Invocations          = var.health_check_lambda_invocations_threshold
      Errors               = var.health_check_lambda_errors_threshold
    }
  }

  # Lambda function mapping
  lambda_functions = {
    search_lambda       = module.lambda.lambda_function_name
    health_check_lambda = module.health_check_lambda.lambda_function_name
  }

  # Generate alarms from JSON config
  alarms = merge([
    for lambda_type, alarm_configs in local.alarm_config : {
      for alarm in alarm_configs :
      "${lambda_type}_${replace(lower(alarm.metric_name), "/[^a-z0-9]/", "_")}" => {
        function_name       = local.lambda_functions[lambda_type]
        metric_name         = alarm.metric_name
        statistic           = alarm.statistic
        threshold           = local.thresholds[lambda_type][alarm.metric_name]
        comparison_operator = alarm.comparison_operator
        alarm_name          = "${local.resource_prefix}-${replace(lambda_type, "_", "-")}-${alarm.alarm_suffix}"
        description         = alarm.description
      }
    }
  ]...)
}

module "cloudwatch_alarms" {
  for_each = local.alarms
  source   = "../../modules/cloudwatch-alarm"

  alarm_name          = each.value.alarm_name
  comparison_operator = each.value.comparison_operator
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = each.value.metric_name
  period              = var.lambda_alarm_period
  statistic           = each.value.statistic
  threshold           = each.value.threshold
  alarm_description   = each.value.description
  sns_topic_arn       = module.sns.topic_arn
  function_name       = each.value.function_name
  workspace_suffix    = local.workspace_suffix
  namespace           = "AWS/Lambda"
  treat_missing_data  = "notBreaching"
}
