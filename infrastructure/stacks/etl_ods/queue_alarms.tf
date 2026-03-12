module "etl_ods_queue_alarms" {
  #TODO: Allowing to be workspaced to enable testing. Will uncomment once tested.
  # count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix # Used for naming SNS topic and alarms

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "DoS Search Alarms"
  kms_key_id       = data.aws_kms_key.sns_kms_key.arn

  # Enable Slack notifications
  slack_notifier_enabled       = true
  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  alarm_config_path = "dlq/config"

  monitored_resources = {
    transformer_dlq   = aws_sqs_queue.transform_dead_letter_queue.name
    consume_dlq       = aws_sqs_queue.load_dead_letter_queue.name
    transformer_queue = aws_sqs_queue.transform_queue.name
    consumer_queue    = aws_sqs_queue.load_queue.name
  }

  alarm_thresholds = {
    transformer_dlq = {
      "messages-count" = 0
    }
    consumer_dlq = {
      "messages-count" = 0
    }
    transformer_queue = {
      "messages-age" = var.transform_queue_age_threshold_seconds
    }
    consumer_queue = {
      "messages-age" = var.load_queue_age_threshold_seconds
    }
  }

  alarm_evaluation_periods = {
    transformer_dlq = {
      "messages-count" = 1
    }
    consumer_dlq = {
      "messages-count" = 1
    }
    transformer_queue = {
      "messages-age" = 2
    }
    consumer_queue = {
      "messages-age" = 2
    }
  }

  alarm_periods = {
    transformer_dlq = {
      "messages-count" = 300
    }
    consumer_dlq = {
      "messages-count" = 300
    }
    transformer_queue = {
      "messages-age" = 300
    }
    consumer_queue = {
      "messages-age" = 300
    }
  }
}