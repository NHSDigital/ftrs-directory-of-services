################################################################################
# AppConfig Integration for CloudWatch Alarm Thresholds
################################################################################
#
# DEPLOYMENT WORKFLOW:
#
# Initial Setup (One-time):
#   1. terraform apply (app_config stack) → Creates AppConfig application
#   2. terraform apply (dos_search stack)  → Reads initial config & creates alarms
#
# Ongoing Updates (No Redeployment):
#   1. Update thresholds via AWS AppConfig GUI
#   2. terraform apply (dos_search stack) → Picks up live AppConfig values
#
# How it works:
#   - AppConfig is the SOURCE OF TRUTH for alarm thresholds
#   - Terraform reads LIVE values from AppConfig (not local files)
#   - Operational teams can update AppConfig via GUI without code/Git changes
#   - Next terraform apply detects and applies changes to CloudWatch alarms
#   - Full audit trail available in both AWS AppConfig and Terraform state
#
################################################################################

# Parse the live AppConfig JSON response and define CloudWatch alarms
locals {
  # Decode the JSON content from AppConfig remote state
  alarm_config = jsondecode(data.terraform_remote_state.app_config.outputs.alarm_thresholds_content)

  # Search Lambda thresholds from LIVE AppConfig
  search_lambda_duration_threshold_ms           = local.alarm_config.searchLambda.duration.threshold_ms
  search_lambda_concurrent_executions_threshold = local.alarm_config.searchLambda.concurrentExecutions.threshold
  search_lambda_errors_threshold                = local.alarm_config.searchLambda.errors.threshold
  search_lambda_invocations_threshold           = local.alarm_config.searchLambda.invocations.threshold
  search_lambda_throttles_threshold             = local.alarm_config.searchLambda.throttles.threshold

  # Health Check Lambda thresholds from LIVE AppConfig
  health_check_lambda_duration_threshold_ms           = local.alarm_config.healthCheckLambda.duration.threshold_ms
  health_check_lambda_concurrent_executions_threshold = local.alarm_config.healthCheckLambda.concurrentExecutions.threshold
  health_check_lambda_errors_threshold                = local.alarm_config.healthCheckLambda.errors.threshold
  health_check_lambda_invocations_threshold           = local.alarm_config.healthCheckLambda.invocations.threshold
  health_check_lambda_throttles_threshold             = local.alarm_config.healthCheckLambda.throttles.threshold

  # Shared alarm configuration from LIVE AppConfig
  lambda_alarm_evaluation_periods = local.alarm_config.alarmConfiguration.evaluationPeriods
  lambda_alarm_period             = local.alarm_config.alarmConfiguration.periodSeconds

  # CloudWatch Alarms configuration
  alarms = {
    # Search Lambda Alarms
    search_lambda_duration = {
      function_name       = module.lambda.lambda_function_name
      metric_name         = "Duration"
      statistic           = "Average"
      threshold           = local.search_lambda_duration_threshold_ms
      comparison_operator = "GreaterThanThreshold"
      alarm_name          = "${local.resource_prefix}-search-lambda-duration-high"
      description         = "Alert when search Lambda average duration exceeds threshold (${local.search_lambda_duration_threshold_ms}ms). Managed via AppConfig."
    }
    search_lambda_concurrent_executions = {
      function_name       = module.lambda.lambda_function_name
      metric_name         = "ConcurrentExecutions"
      statistic           = "Maximum"
      threshold           = local.search_lambda_concurrent_executions_threshold
      comparison_operator = "GreaterThanThreshold"
      alarm_name          = "${local.resource_prefix}-search-lambda-concurrent-executions-high"
      description         = "Alert when search Lambda concurrent executions exceed threshold (${local.search_lambda_concurrent_executions_threshold}). Managed via AppConfig."
    }
    search_lambda_throttles = {
      function_name       = module.lambda.lambda_function_name
      metric_name         = "Throttles"
      statistic           = "Sum"
      threshold           = local.search_lambda_throttles_threshold
      comparison_operator = "GreaterThanOrEqualToThreshold"
      alarm_name          = "${local.resource_prefix}-search-lambda-throttles"
      description         = "Alert when search Lambda is throttled (threshold: ${local.search_lambda_throttles_threshold}). Managed via AppConfig."
    }
    search_lambda_invocations = {
      function_name       = module.lambda.lambda_function_name
      metric_name         = "Invocations"
      statistic           = "Sum"
      threshold           = local.search_lambda_invocations_threshold
      comparison_operator = "LessThanThreshold"
      alarm_name          = "${local.resource_prefix}-search-lambda-invocations-low"
      description         = "Alert when search Lambda invocations fall below expected threshold (${local.search_lambda_invocations_threshold}). Managed via AppConfig."
    }
    search_lambda_errors = {
      function_name       = module.lambda.lambda_function_name
      metric_name         = "Errors"
      statistic           = "Sum"
      threshold           = local.search_lambda_errors_threshold
      comparison_operator = "GreaterThanThreshold"
      alarm_name          = "${local.resource_prefix}-search-lambda-errors"
      description         = "Alert when search Lambda errors exceed threshold (${local.search_lambda_errors_threshold}). Managed via AppConfig."
    }
    # Health Check Lambda Alarms
    health_check_lambda_duration = {
      function_name       = module.health_check_lambda.lambda_function_name
      metric_name         = "Duration"
      statistic           = "Average"
      threshold           = local.health_check_lambda_duration_threshold_ms
      comparison_operator = "GreaterThanThreshold"
      alarm_name          = "${local.resource_prefix}-health-check-lambda-duration-high"
      description         = "Alert when health check Lambda average duration exceeds threshold (${local.health_check_lambda_duration_threshold_ms}ms). Managed via AppConfig."
    }
    health_check_lambda_concurrent_executions = {
      function_name       = module.health_check_lambda.lambda_function_name
      metric_name         = "ConcurrentExecutions"
      statistic           = "Maximum"
      threshold           = local.health_check_lambda_concurrent_executions_threshold
      comparison_operator = "GreaterThanThreshold"
      alarm_name          = "${local.resource_prefix}-health-check-lambda-concurrent-executions-high"
      description         = "Alert when health check Lambda concurrent executions exceed threshold (${local.health_check_lambda_concurrent_executions_threshold}). Managed via AppConfig."
    }
    health_check_lambda_throttles = {
      function_name       = module.health_check_lambda.lambda_function_name
      metric_name         = "Throttles"
      statistic           = "Sum"
      threshold           = local.health_check_lambda_throttles_threshold
      comparison_operator = "GreaterThanOrEqualToThreshold"
      alarm_name          = "${local.resource_prefix}-health-check-lambda-throttles"
      description         = "Alert when health check Lambda is throttled (threshold: ${local.health_check_lambda_throttles_threshold}). Managed via AppConfig."
    }
    health_check_lambda_invocations = {
      function_name       = module.health_check_lambda.lambda_function_name
      metric_name         = "Invocations"
      statistic           = "Sum"
      threshold           = local.health_check_lambda_invocations_threshold
      comparison_operator = "LessThanThreshold"
      alarm_name          = "${local.resource_prefix}-health-check-lambda-invocations-low"
      description         = "Alert when health check Lambda invocations fall below expected threshold (${local.health_check_lambda_invocations_threshold}). Managed via AppConfig."
    }
    health_check_lambda_errors = {
      function_name       = module.health_check_lambda.lambda_function_name
      metric_name         = "Errors"
      statistic           = "Sum"
      threshold           = local.health_check_lambda_errors_threshold
      comparison_operator = "GreaterThanThreshold"
      alarm_name          = "${local.resource_prefix}-health-check-lambda-errors"
      description         = "Alert when health check Lambda errors exceed threshold (${local.health_check_lambda_errors_threshold}). Managed via AppConfig."
    }
  }
}

module "cloudwatch_alarms" {
  for_each = local.alarms

  source = "../../modules/cloudwatch-alarm"

  alarm_name          = each.value.alarm_name
  comparison_operator = each.value.comparison_operator
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = each.value.metric_name
  period              = local.lambda_alarm_period
  statistic           = each.value.statistic
  threshold           = each.value.threshold
  alarm_description   = each.value.description
  sns_topic_arn       = module.sns.topic_arn
  function_name       = each.value.function_name
  workspace_suffix    = local.workspace_suffix
  namespace           = "AWS/Lambda"
  treat_missing_data  = "notBreaching"
}
