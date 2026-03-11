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


# The CloudFront certificate lives in us-east-1 (AWS requirement). Rather than
# creating a separate SNS topic + Slack Lambda there, these alarms send their
# actions directly to the eu-west-2 SNS topic created by acm_api_cert_alarms.
# CloudWatch alarms support cross-region SNS targets natively, and the eu-west-2
# SNS policy already permits cloudwatch.amazonaws.com to publish (no region
# restriction on the service principal).

resource "aws_cloudwatch_metric_alarm" "acm_cloudfront_cert_days_to_expiry_warning" {
  count    = var.environment == "mgmt" ? 0 : 1
  provider = aws.us-east-1

  alarm_name          = "${local.resource_prefix}-cloudfront-cert-days-to-expiry-warning"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.acm_days_to_expiry_warning_alarm_evaluation_periods
  metric_name         = "DaysToExpiry"
  namespace           = "AWS/CertificateManager"
  period              = var.acm_days_to_expiry_warning_alarm_period
  statistic           = "Minimum"
  threshold           = var.acm_days_to_expiry_warning_alarm_threshold
  alarm_description   = "ACM Certificate expiry warning - certificate expires in less than ${var.acm_days_to_expiry_warning_alarm_threshold} days"
  treat_missing_data  = "notBreaching"
  actions_enabled     = var.enable_warning_alarms

  alarm_actions = [module.acm_api_cert_alarms[0].sns_topic_arn]

  dimensions = {
    CertificateArn = aws_acm_certificate.custom_domain_cert_cloudfront[0].arn
  }

  tags = {
    Name = "${local.resource_prefix}-cloudfront-cert-days-to-expiry-warning"
  }
}

resource "aws_cloudwatch_metric_alarm" "acm_cloudfront_cert_days_to_expiry_critical" {
  count    = var.environment == "mgmt" ? 0 : 1
  provider = aws.us-east-1

  alarm_name          = "${local.resource_prefix}-cloudfront-cert-days-to-expiry-critical"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.acm_days_to_expiry_critical_alarm_evaluation_periods
  metric_name         = "DaysToExpiry"
  namespace           = "AWS/CertificateManager"
  period              = var.acm_days_to_expiry_critical_alarm_period
  statistic           = "Minimum"
  threshold           = var.acm_days_to_expiry_critical_alarm_threshold
  alarm_description   = "ACM Certificate expiry critical - certificate expires in less than ${var.acm_days_to_expiry_critical_alarm_threshold} days"
  treat_missing_data  = "notBreaching"
  actions_enabled     = true

  alarm_actions = [module.acm_api_cert_alarms[0].sns_topic_arn]

  dimensions = {
    CertificateArn = aws_acm_certificate.custom_domain_cert_cloudfront[0].arn
  }

  tags = {
    Name = "${local.resource_prefix}-cloudfront-cert-days-to-expiry-critical"
  }
}
