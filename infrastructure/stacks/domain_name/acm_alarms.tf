module "acm_api_cert_alarms" {
  count  = var.environment == "mgmt" ? 0 : 1
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "ACM API Certificate Alarms"
  kms_key_id       = data.aws_kms_key.sns_kms_key.arn

  alarm_config_path = "acm/config"

  monitored_resources = {
    api_cert = aws_acm_certificate.custom_domain_api_cert[0].arn
  }

  resource_metadata = {}

  resource_additional_dimensions = {}

  alarm_thresholds = {
    api_cert = {
      "days-to-expiry-warning"  = var.acm_days_to_expiry_warning_alarm_threshold
      "days-to-expiry-critical" = var.acm_days_to_expiry_critical_alarm_threshold
    }
  }

  alarm_evaluation_periods = {
    api_cert = {
      "days-to-expiry-warning"  = var.acm_days_to_expiry_warning_alarm_evaluation_periods
      "days-to-expiry-critical" = var.acm_days_to_expiry_critical_alarm_evaluation_periods
    }
  }

  alarm_periods = {
    api_cert = {
      "days-to-expiry-warning"  = var.acm_days_to_expiry_warning_alarm_period
      "days-to-expiry-critical" = var.acm_days_to_expiry_critical_alarm_period
    }
  }

  enable_warning_alarms = var.enable_warning_alarms

  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  tags = {
    Name = "${local.resource_prefix}-acm-api-cert-alarms"
  }
}

module "acm_cloudfront_cert_alarms" {
  count  = var.environment == "mgmt" ? 0 : 1
  source = "../../modules/cloudwatch-monitoring"

  providers = {
    aws = aws.us-east-1
  }

  resource_prefix = local.resource_prefix

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "ACM CloudFront Certificate Alarms"
  kms_key_id       = data.aws_kms_key.sns_kms_key.arn

  alarm_config_path = "acm/config"

  monitored_resources = {
    cloudfront_cert = aws_acm_certificate.custom_domain_cert_cloudfront[0].arn
  }

  resource_metadata = {}

  resource_additional_dimensions = {}

  alarm_thresholds = {
    cloudfront_cert = {
      "days-to-expiry-warning"  = var.acm_days_to_expiry_warning_alarm_threshold
      "days-to-expiry-critical" = var.acm_days_to_expiry_critical_alarm_threshold
    }
  }

  alarm_evaluation_periods = {
    cloudfront_cert = {
      "days-to-expiry-warning"  = var.acm_days_to_expiry_warning_alarm_evaluation_periods
      "days-to-expiry-critical" = var.acm_days_to_expiry_critical_alarm_evaluation_periods
    }
  }

  alarm_periods = {
    cloudfront_cert = {
      "days-to-expiry-warning"  = var.acm_days_to_expiry_warning_alarm_period
      "days-to-expiry-critical" = var.acm_days_to_expiry_critical_alarm_period
    }
  }

  enable_warning_alarms = var.enable_warning_alarms

  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  tags = {
    Name = "${local.resource_prefix}-acm-cloudfront-cert-alarms"
  }
}
