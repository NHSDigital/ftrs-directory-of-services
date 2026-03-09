################################################################################
# CloudWatch Monitoring Module for ETL ODS Lambdas
################################################################################

module "etl_ods_lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix   = local.resource_prefix
  sns_topic_name    = local.alarms_topic_name
  sns_display_name  = "ETL ODS Lambda Alarms"
  kms_key_id        = data.aws_kms_key.sns_kms_key.arn
  alarm_config_path = "lambda/config"

  # Enable Slack notifications
  slack_notifier_enabled       = true
  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  monitored_resources = {
    extractor   = module.extractor_lambda.lambda_function_name
    transformer = module.transformer_lambda.lambda_function_name
    consumer    = module.consumer_lambda.lambda_function_name
  }

  resource_metadata = {
    extractor = {
      api_path = "eventbridge:scheduled" # Triggered by EventBridge daily schedule
      service  = "ETL ODS Extractor"
    }
    transformer = {
      api_path = "sqs:transform-queue" # Triggered by Transform SQS queue
      service  = "ETL ODS Transformer"
    }
    consumer = {
      api_path = "sqs:load-queue" # Triggered by Load SQS queue
      service  = "ETL ODS Consumer"
    }
  }

  alarm_thresholds = {
    extractor = {
      "duration-p95-warning"           = var.extractor_duration_p95_warning_ms
      "duration-p99-critical"          = var.extractor_duration_p99_critical_ms
      "errors-warning"                 = var.extractor_errors_warning_threshold
      "errors-critical"                = var.extractor_errors_critical_threshold
      "throttles-critical"             = var.extractor_throttles_critical_threshold
      "concurrent-executions-warning"  = var.extractor_concurrent_executions_warning
      "concurrent-executions-critical" = var.extractor_concurrent_executions_critical
      "invocations-spike-critical"     = var.extractor_invocations_spike_critical
    }
    transformer = {
      "duration-p95-warning"           = var.transformer_duration_p95_warning_ms
      "duration-p99-critical"          = var.transformer_duration_p99_critical_ms
      "errors-warning"                 = var.transformer_errors_warning_threshold
      "errors-critical"                = var.transformer_errors_critical_threshold
      "throttles-critical"             = var.transformer_throttles_critical_threshold
      "concurrent-executions-warning"  = var.transformer_concurrent_executions_warning
      "concurrent-executions-critical" = var.transformer_concurrent_executions_critical
      "invocations-spike-critical"     = var.transformer_invocations_spike_critical
    }
    consumer = {
      "duration-p95-warning"           = var.consumer_duration_p95_warning_ms
      "duration-p99-critical"          = var.consumer_duration_p99_critical_ms
      "errors-warning"                 = var.consumer_errors_warning_threshold
      "errors-critical"                = var.consumer_errors_critical_threshold
      "throttles-critical"             = var.consumer_throttles_critical_threshold
      "concurrent-executions-warning"  = var.consumer_concurrent_executions_warning
      "concurrent-executions-critical" = var.consumer_concurrent_executions_critical
      "invocations-spike-critical"     = var.consumer_invocations_spike_critical
    }
  }

  alarm_evaluation_periods = {
    extractor = {
      "duration-p95-warning"           = var.lambda_alarm_evaluation_periods
      "duration-p99-critical"          = var.lambda_alarm_evaluation_periods
      "errors-warning"                 = var.lambda_alarm_evaluation_periods
      "errors-critical"                = var.lambda_alarm_evaluation_periods
      "throttles-critical"             = var.lambda_throttles_evaluation_periods
      "concurrent-executions-warning"  = var.lambda_alarm_evaluation_periods
      "concurrent-executions-critical" = var.lambda_alarm_evaluation_periods
      "invocations-spike-critical"     = var.lambda_alarm_evaluation_periods
    }
    transformer = {
      "duration-p95-warning"           = var.lambda_alarm_evaluation_periods
      "duration-p99-critical"          = var.lambda_alarm_evaluation_periods
      "errors-warning"                 = var.lambda_alarm_evaluation_periods
      "errors-critical"                = var.lambda_alarm_evaluation_periods
      "throttles-critical"             = var.lambda_throttles_evaluation_periods
      "concurrent-executions-warning"  = var.lambda_alarm_evaluation_periods
      "concurrent-executions-critical" = var.lambda_alarm_evaluation_periods
      "invocations-spike-critical"     = var.lambda_alarm_evaluation_periods
    }
    consumer = {
      "duration-p95-warning"           = var.lambda_alarm_evaluation_periods
      "duration-p99-critical"          = var.lambda_alarm_evaluation_periods
      "errors-warning"                 = var.lambda_alarm_evaluation_periods
      "errors-critical"                = var.lambda_alarm_evaluation_periods
      "throttles-critical"             = var.lambda_throttles_evaluation_periods
      "concurrent-executions-warning"  = var.lambda_alarm_evaluation_periods
      "concurrent-executions-critical" = var.lambda_alarm_evaluation_periods
      "invocations-spike-critical"     = var.lambda_alarm_evaluation_periods
    }
  }

  alarm_periods = {
    extractor = {
      "duration-p95-warning"           = var.lambda_alarm_period_seconds
      "duration-p99-critical"          = var.lambda_alarm_period_seconds
      "errors-warning"                 = var.lambda_alarm_period_seconds
      "errors-critical"                = var.lambda_alarm_period_seconds
      "throttles-critical"             = var.lambda_throttles_period_seconds
      "concurrent-executions-warning"  = var.lambda_alarm_period_seconds
      "concurrent-executions-critical" = var.lambda_alarm_period_seconds
      "invocations-spike-critical"     = var.invocations_spike_period_seconds
    }
    transformer = {
      "duration-p95-warning"           = var.lambda_alarm_period_seconds
      "duration-p99-critical"          = var.lambda_alarm_period_seconds
      "errors-warning"                 = var.lambda_alarm_period_seconds
      "errors-critical"                = var.lambda_alarm_period_seconds
      "throttles-critical"             = var.lambda_throttles_period_seconds
      "concurrent-executions-warning"  = var.lambda_alarm_period_seconds
      "concurrent-executions-critical" = var.lambda_alarm_period_seconds
      "invocations-spike-critical"     = var.invocations_spike_period_seconds
    }
    consumer = {
      "duration-p95-warning"           = var.lambda_alarm_period_seconds
      "duration-p99-critical"          = var.lambda_alarm_period_seconds
      "errors-warning"                 = var.lambda_alarm_period_seconds
      "errors-critical"                = var.lambda_alarm_period_seconds
      "throttles-critical"             = var.lambda_throttles_period_seconds
      "concurrent-executions-warning"  = var.lambda_alarm_period_seconds
      "concurrent-executions-critical" = var.lambda_alarm_period_seconds
      "invocations-spike-critical"     = var.invocations_spike_period_seconds
    }
  }

  enable_warning_alarms = var.enable_warning_alarms

  tags = {
    Name = local.alarms_topic_name
  }
}

################################################################################
# SQS Queue Alarms (AWS Automatic Metrics)
################################################################################

# Transform DLQ messages alarm
resource "aws_cloudwatch_metric_alarm" "transform_dlq_messages" {
  alarm_name          = "${local.resource_prefix}-transform-dlq-messages${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "Alert when messages appear in Transform DLQ"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.etl_ods_lambda_monitoring.sns_topic_arn]

  dimensions = {
    QueueName = aws_sqs_queue.transform_dead_letter_queue.name
  }

  tags = {
    Name        = "${local.resource_prefix}-transform-dlq-messages${local.workspace_suffix}"
    Service     = var.service
    Environment = var.environment
    Stack       = var.stack_name
    Component   = "transformer"
  }
}

# Load DLQ messages alarm
resource "aws_cloudwatch_metric_alarm" "load_dlq_messages" {
  alarm_name          = "${local.resource_prefix}-load-dlq-messages${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "Alert when messages appear in Load DLQ"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.etl_ods_lambda_monitoring.sns_topic_arn]

  dimensions = {
    QueueName = aws_sqs_queue.load_dead_letter_queue.name
  }

  tags = {
    Name        = "${local.resource_prefix}-load-dlq-messages${local.workspace_suffix}"
    Service     = var.service
    Environment = var.environment
    Stack       = var.stack_name
    Component   = "consumer"
  }
}

# Transform Queue age alarm
resource "aws_cloudwatch_metric_alarm" "transform_queue_age" {
  alarm_name          = "${local.resource_prefix}-transform-queue-age${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ApproximateAgeOfOldestMessage"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = var.transform_queue_age_threshold_seconds
  alarm_description   = "Alert when Transform Queue messages are too old"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.etl_ods_lambda_monitoring.sns_topic_arn]

  dimensions = {
    QueueName = aws_sqs_queue.transform_queue.name
  }

  tags = {
    Name        = "${local.resource_prefix}-transform-queue-age${local.workspace_suffix}"
    Service     = var.service
    Environment = var.environment
    Stack       = var.stack_name
    Component   = "transformer"
  }
}

# Load Queue age alarm
resource "aws_cloudwatch_metric_alarm" "load_queue_age" {
  alarm_name          = "${local.resource_prefix}-load-queue-age${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ApproximateAgeOfOldestMessage"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = var.load_queue_age_threshold_seconds
  alarm_description   = "Alert when Load Queue messages are too old"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.etl_ods_lambda_monitoring.sns_topic_arn]

  dimensions = {
    QueueName = aws_sqs_queue.load_queue.name
  }

  tags = {
    Name        = "${local.resource_prefix}-load-queue-age${local.workspace_suffix}"
    Service     = var.service
    Environment = var.environment
    Stack       = var.stack_name
    Component   = "consumer"
  }
}
