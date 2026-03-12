module "s3_alarms" {
  count  = local.is_primary_environment ? 1 : 0
  source = "../../modules/cloudwatch-monitoring"

  providers = {
    aws.metrics = aws
    aws.sns     = aws
    aws.lambda  = aws
  }

  resource_prefix = local.resource_prefix # Used for naming SNS topic and alarms

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "S3 Account Wide Alarms"
  kms_key_id       = data.aws_kms_key.sns_kms_key[0].arn

  alarm_config_path = "s3/config"

  monitored_resources = {
    truststore_s3      = data.aws_s3_bucket.trust_store_s3_bucket.id
    terraform_state_s3 = data.aws_s3_bucket.terraform_state_bucket.id
  }

  resource_metadata = {}

  resource_additional_dimensions = {
    truststore_s3 = {
      "FilterId" = "EntireBucket"
    }
    terraform_state_s3 = {
      "FilterId" = "EntireBucket"
    }
  }

  alarm_thresholds = {
    truststore_s3 = {
      "5xx-errors-warning"  = var.truststore_s3_5xx_errors_warning_alarm_threshold
      "5xx-errors-critical" = var.truststore_s3_5xx_errors_critical_alarm_threshold
      "4xx-errors-warning"  = var.truststore_s3_4xx_errors_warning_alarm_threshold
      "4xx-errors-critical" = var.truststore_s3_4xx_errors_critical_alarm_threshold
    }
    terraform_state_s3 = {
      "5xx-errors-warning"  = var.terraform_state_s3_5xx_errors_warning_alarm_threshold
      "5xx-errors-critical" = var.terraform_state_s3_5xx_errors_critical_alarm_threshold
      "4xx-errors-warning"  = var.terraform_state_s3_4xx_errors_warning_alarm_threshold
      "4xx-errors-critical" = var.terraform_state_s3_4xx_errors_critical_alarm_threshold
    }
  }

  alarm_evaluation_periods = {
    truststore_s3 = {
      "5xx-errors-warning"  = var.truststore_s3_5xx_errors_warning_alarm_evaluation_periods
      "5xx-errors-critical" = var.truststore_s3_5xx_errors_critical_alarm_evaluation_periods
      "4xx-errors-warning"  = var.truststore_s3_4xx_errors_warning_alarm_evaluation_periods
      "4xx-errors-critical" = var.truststore_s3_4xx_errors_critical_alarm_evaluation_periods
    }
    terraform_state_s3 = {
      "5xx-errors-warning"  = var.terraform_state_s3_5xx_errors_warning_alarm_evaluation_periods
      "5xx-errors-critical" = var.terraform_state_s3_5xx_errors_critical_alarm_evaluation_periods
      "4xx-errors-warning"  = var.terraform_state_s3_4xx_errors_warning_alarm_evaluation_periods
      "4xx-errors-critical" = var.terraform_state_s3_4xx_errors_critical_alarm_evaluation_periods
    }
  }

  alarm_periods = {
    truststore_s3 = {
      "5xx-errors-warning"  = var.truststore_s3_5xx_errors_warning_alarm_period
      "5xx-errors-critical" = var.truststore_s3_5xx_errors_critical_alarm_period
      "4xx-errors-warning"  = var.truststore_s3_4xx_errors_warning_alarm_period
      "4xx-errors-critical" = var.truststore_s3_4xx_errors_critical_alarm_period
    }
    terraform_state_s3 = {
      "5xx-errors-warning"  = var.terraform_state_s3_5xx_errors_warning_alarm_period
      "5xx-errors-critical" = var.terraform_state_s3_5xx_errors_critical_alarm_period
      "4xx-errors-warning"  = var.terraform_state_s3_4xx_errors_warning_alarm_period
      "4xx-errors-critical" = var.terraform_state_s3_4xx_errors_critical_alarm_period
    }
  }

  slack_notifier_function_name = local.slack_notifier_function_name

  tags = {
    Name = "${local.resource_prefix}-s3-alarms"
  }
}
