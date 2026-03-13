module "acm_api_cert_alarms" {
  count  = var.environment == "mgmt" ? 0 : 1
  source = "../../modules/cloudwatch-monitoring"

  providers = {
    aws.metrics = aws
    aws.sns     = aws
    aws.lambda  = aws
  }

  resource_prefix = local.resource_prefix

  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "ACM API Certificate Alarms"
  kms_key_id       = data.aws_kms_key.sns_kms_key[0].arn

  alarm_config_path = "acm/config"

  monitored_resources = {
    api_cert = data.aws_acm_certificate.custom_domain_api_cert[0].arn
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

  slack_notifier_function_name = local.slack_notifier_function_name

  tags = {
    Name = "${local.resource_prefix}-acm-api-cert-alarms"
  }
}

# The CloudFront certificate lives in us-east-1 (AWS requirement).
# Alarms are created in us-east-1 via aws.us-east-1 (aws.metrics).
# They target a new SNS topic also in us-east-1 (aws.sns = aws.us-east-1).
# The Slack notifier Lambda lives in eu-west-2; SNS cross-region Lambda
# subscriptions are supported, so aws.lambda points to the default provider.
module "acm_cloudfront_cert_alarms" {
  count  = var.environment == "mgmt" ? 0 : 1
  source = "../../modules/cloudwatch-monitoring"

  providers = {
    aws.metrics = aws.us-east-1
    aws.sns     = aws.us-east-1
    aws.lambda  = aws
  }

  resource_prefix  = local.resource_prefix
  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "ACM CloudFront Certificate Alarms"

  alarm_config_path = "acm/config"

  monitored_resources = {
    cloudfront_cert = data.aws_acm_certificate.custom_domain_cert_cloudfront[0].arn
  }

  resource_metadata              = {}
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

  slack_notifier_function_name = local.slack_notifier_function_name

  tags = {
    Name = "${local.resource_prefix}-acm-cloudfront-cert-alarms"
  }
}
