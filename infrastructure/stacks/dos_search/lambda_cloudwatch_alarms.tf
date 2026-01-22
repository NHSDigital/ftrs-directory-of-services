################################################################################
# CloudWatch Alarms for dos-search Lambda Functions
################################################################################

# SNS Topic for Slack notifications
resource "aws_sns_topic" "dos_search_lambda_alarms" {
  name              = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  display_name      = "DoS Search Lambda Alarms"
  kms_master_key_id = "alias/aws/sns"

  tags = local.common_tags
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
resource "aws_cloudwatch_metric_alarm" "search_lambda_duration" {
  alarm_name          = "${local.resource_prefix}-search-lambda-duration-high${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Average"
  threshold           = var.search_lambda_duration_threshold_ms
  alarm_description   = "Alert when search Lambda average duration exceeds threshold"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = local.common_tags
}

# Concurrent Executions Alarm - triggers if concurrent executions exceed threshold
resource "aws_cloudwatch_metric_alarm" "search_lambda_concurrent_executions" {
  alarm_name          = "${local.resource_prefix}-search-lambda-concurrent-executions-high${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "ConcurrentExecutions"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Maximum"
  threshold           = var.search_lambda_concurrent_executions_threshold
  alarm_description   = "Alert when search Lambda concurrent executions exceed threshold"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = local.common_tags
}

# Throttles Alarm - triggers if any throttles occur
resource "aws_cloudwatch_metric_alarm" "search_lambda_throttles" {
  alarm_name          = "${local.resource_prefix}-search-lambda-throttles${local.workspace_suffix}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alert when search Lambda is throttled"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = local.common_tags
}

# Invocations Alarm - optional: tracks invocation rate
resource "aws_cloudwatch_metric_alarm" "search_lambda_invocations" {
  alarm_name          = "${local.resource_prefix}-search-lambda-invocations-low${local.workspace_suffix}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "Invocations"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Sum"
  threshold           = var.search_lambda_invocations_threshold
  alarm_description   = "Alert when search Lambda invocations fall below expected threshold"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = local.common_tags
}

# Errors Alarm - triggers if error rate exceeds threshold
resource "aws_cloudwatch_metric_alarm" "search_lambda_errors" {
  alarm_name          = "${local.resource_prefix}-search-lambda-errors${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Sum"
  threshold           = var.search_lambda_errors_threshold
  alarm_description   = "Alert when search Lambda errors exceed threshold"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda.lambda_function_name
  }

  tags = local.common_tags
}

################################################################################
# Health Check Lambda Alarms
################################################################################

# Duration Alarm
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_duration" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-duration-high${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Average"
  threshold           = var.health_check_lambda_duration_threshold_ms
  alarm_description   = "Alert when health check Lambda average duration exceeds threshold"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = local.common_tags
}

# Concurrent Executions Alarm
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_concurrent_executions" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-concurrent-executions-high${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "ConcurrentExecutions"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Maximum"
  threshold           = var.health_check_lambda_concurrent_executions_threshold
  alarm_description   = "Alert when health check Lambda concurrent executions exceed threshold"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = local.common_tags
}

# Throttles Alarm
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_throttles" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-throttles${local.workspace_suffix}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alert when health check Lambda is throttled"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = local.common_tags
}

# Invocations Alarm
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_invocations" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-invocations-low${local.workspace_suffix}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "Invocations"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Sum"
  threshold           = var.health_check_lambda_invocations_threshold
  alarm_description   = "Alert when health check Lambda invocations fall below expected threshold"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = local.common_tags
}

# Errors Alarm
resource "aws_cloudwatch_metric_alarm" "health_check_lambda_errors" {
  alarm_name          = "${local.resource_prefix}-health-check-lambda-errors${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.lambda_alarm_evaluation_periods
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = var.lambda_alarm_period
  statistic           = "Sum"
  threshold           = var.health_check_lambda_errors_threshold
  alarm_description   = "Alert when health check Lambda errors exceed threshold"
  alarm_actions       = [aws_sns_topic.dos_search_lambda_alarms.arn]
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.health_check_lambda.lambda_function_name
  }

  tags = local.common_tags
}
