################################################################################
# CloudWatch Alarms for dos-search Lambda Functions
################################################################################

# SNS Topic for Slack notifications
resource "aws_sns_topic" "dos_search_lambda_alarms" {
  name              = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  display_name      = "DoS Search Lambda Alarms"
  kms_master_key_id = "alias/aws/sns"

  tags = {
    Name = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  }
}

# SNS Topic Policy to allow CloudWatch to publish
resource "aws_sns_topic_policy" "dos_search_lambda_alarms_policy" {
  arn = aws_sns_topic.dos_search_lambda_alarms.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.dos_search_lambda_alarms.arn
      }
    ]
  })
}

################################################################################
# Search Lambda Alarms
################################################################################

# Duration Alarm - triggers if average duration exceeds threshold
# Threshold is sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "search_lambda_duration" {
  alarm_name          = "${local.resource_prefix}-search-lambda-duration-high${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Average"
  threshold           = local.search_lambda_duration_threshold_ms
  alarm_description   = "Alert when search Lambda average duration exceeds threshold (${local.search_lambda_duration_threshold_ms}ms). Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-search-lambda-duration-high${local.workspace_suffix}"
  }
}

# Concurrent Executions Alarm - triggers if concurrent executions exceed threshold
# Threshold is sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "search_lambda_concurrent_executions" {
  alarm_name          = "${local.resource_prefix}-search-lambda-concurrent-executions-high${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "ConcurrentExecutions"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Maximum"
  threshold           = local.search_lambda_concurrent_executions_threshold
  alarm_description   = "Alert when search Lambda concurrent executions exceed threshold (${local.search_lambda_concurrent_executions_threshold}). Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-search-lambda-concurrent-executions-high${local.workspace_suffix}"
  }
}

# Throttles Alarm - triggers if any throttles occur
# Evaluation periods sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "search_lambda_throttles" {
  alarm_name          = "${local.resource_prefix}-search-lambda-throttles${local.workspace_suffix}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alert when search Lambda is throttled. Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-search-lambda-throttles${local.workspace_suffix}"
  }
}

# Invocations Alarm - optional: tracks invocation rate
# Threshold is sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "search_lambda_invocations" {
  alarm_name          = "${local.resource_prefix}-search-lambda-invocations-low${local.workspace_suffix}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "Invocations"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Sum"
  threshold           = local.search_lambda_invocations_threshold
  alarm_description   = "Alert when search Lambda invocations fall below expected threshold (${local.search_lambda_invocations_threshold}). Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-search-lambda-invocations-low${local.workspace_suffix}"
  }
}

# Errors Alarm - triggers if error rate exceeds threshold
# Threshold is sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "search_lambda_errors" {
  alarm_name          = "${local.resource_prefix}-search-lambda-errors${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Sum"
  threshold           = local.search_lambda_errors_threshold
  alarm_description   = "Alert when search Lambda errors exceed threshold (${local.search_lambda_errors_threshold}). Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-search-lambda-errors${local.workspace_suffix}"
  }
}

################################################################################
# Health Check Lambda Alarms
################################################################################

# Duration Alarm
# Threshold is sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_duration" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-duration-high${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Average"
  threshold           = local.health_check_lambda_duration_threshold_ms
  alarm_description   = "Alert when health check Lambda average duration exceeds threshold (${local.health_check_lambda_duration_threshold_ms}ms). Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-health-check-lambda-duration-high${local.workspace_suffix}"
  }
}

# Concurrent Executions Alarm
# Threshold is sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_concurrent_executions" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-concurrent-executions-high${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "ConcurrentExecutions"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Maximum"
  threshold           = local.health_check_lambda_concurrent_executions_threshold
  alarm_description   = "Alert when health check Lambda concurrent executions exceed threshold (${local.health_check_lambda_concurrent_executions_threshold}). Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-health-check-lambda-concurrent-executions-high${local.workspace_suffix}"
  }
}

# Throttles Alarm
# Evaluation periods sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_throttles" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-throttles${local.workspace_suffix}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alert when health check Lambda is throttled. Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-health-check-lambda-throttles${local.workspace_suffix}"
  }
}

# Invocations Alarm
# Threshold is sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_invocations" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-invocations-low${local.workspace_suffix}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "Invocations"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Sum"
  threshold           = local.health_check_lambda_invocations_threshold
  alarm_description   = "Alert when health check Lambda invocations fall below expected threshold (${local.health_check_lambda_invocations_threshold}). Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-health-check-lambda-invocations-low${local.workspace_suffix}"
  }
}

# Errors Alarm
# Threshold is sourced from AppConfig (toggles/alarm-thresholds.json)
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_errors" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-errors${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = local.lambda_alarm_evaluation_periods
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = local.lambda_alarm_period
  statistic           = "Sum"
  threshold           = local.health_check_lambda_errors_threshold
  alarm_description   = "Alert when health check Lambda errors exceed threshold (${local.health_check_lambda_errors_threshold}). Managed via AppConfig."
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = {
    Name = "${local.resource_prefix}-health-check-lambda-errors${local.workspace_suffix}"
  }
}
