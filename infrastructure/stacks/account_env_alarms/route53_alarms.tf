resource "aws_route53_health_check" "environment_zone" {
  # checkov:skip=CKV2_AWS_49: alarm notification is handled via CloudWatch alarms and SNS
  count             = var.environment == "mgmt" ? 0 : 1
  fqdn              = local.root_domain_name
  port              = 443
  type              = "HTTPS"
  resource_path     = "/"
  failure_threshold = var.route53_health_check_failure_threshold
  request_interval  = var.route53_health_check_request_interval
  measure_latency   = true

  tags = {
    Name = "${local.resource_prefix}-environment-zone-health-check"
  }
}

resource "aws_route53_health_check" "root_zone" {
  # checkov:skip=CKV2_AWS_49: alarm notification is handled via CloudWatch alarms and SNS
  count             = var.environment == "mgmt" ? 0 : 1
  fqdn              = var.root_domain_name
  port              = 443
  type              = "HTTPS"
  resource_path     = "/"
  failure_threshold = var.route53_health_check_failure_threshold
  request_interval  = var.route53_health_check_request_interval
  measure_latency   = true

  tags = {
    Name = "${local.resource_prefix}-root-zone-health-check"
  }
}

# Route 53 health check metrics are published to CloudWatch in us-east-1 only
# (AWS global service constraint). Alarms are created in us-east-1 (aws.metrics).
# The SNS topic and Slack Lambda subscription live in eu-west-2 (aws.sns = aws,
# aws.lambda = aws). CloudWatch alarms natively support cross-region SNS targets.

module "route53_environment_zone_alarms" {
  count  = var.environment == "mgmt" ? 0 : 1
  source = "../../modules/cloudwatch-monitoring"

  providers = {
    aws.metrics = aws.us-east-1
    aws.sns     = aws.us-east-1
    aws.lambda  = aws
  }

  resource_prefix  = local.resource_prefix
  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "Route 53 Environment Zone Alarms"
  kms_key_id       = null

  alarm_config_path = "route53/config"

  monitored_resources = {
    environment_zone = aws_route53_health_check.environment_zone[0].id
  }

  resource_metadata              = {}
  resource_additional_dimensions = {}

  alarm_thresholds = {
    environment_zone = {
      "health-check-status-critical"             = var.route53_health_check_status_critical_alarm_threshold
      "health-check-percentage-healthy-critical" = var.route53_health_check_percentage_healthy_critical_alarm_threshold
    }
  }

  alarm_evaluation_periods = {
    environment_zone = {
      "health-check-status-critical"             = var.route53_health_check_status_critical_alarm_evaluation_periods
      "health-check-percentage-healthy-critical" = var.route53_health_check_percentage_healthy_critical_alarm_evaluation_periods
    }
  }

  alarm_periods = {
    environment_zone = {
      "health-check-status-critical"             = var.route53_health_check_status_critical_alarm_period
      "health-check-percentage-healthy-critical" = var.route53_health_check_percentage_healthy_critical_alarm_period
    }
  }

  slack_notifier_function_name = local.slack_notifier_function_name

  tags = {
    Name = "${local.resource_prefix}-route53-environment-zone-alarms"
  }
}

# Root zone health checks are monitored in the mgmt environment only.
# KMS is omitted as the SNS KMS data source is not active in mgmt.
module "route53_root_zone_alarms" {
  count  = var.environment == "mgmt" ? 1 : 0
  source = "../../modules/cloudwatch-monitoring"

  providers = {
    aws.metrics = aws.us-east-1
    aws.sns     = aws.us-east-1
    aws.lambda  = aws
  }

  resource_prefix  = local.resource_prefix
  sns_topic_name   = local.alarms_topic_name
  sns_display_name = "Route 53 Root Zone Alarms"
  kms_key_id       = null

  alarm_config_path = "route53/config"

  monitored_resources = {
    root_zone = aws_route53_health_check.root_zone[0].id
  }

  resource_metadata              = {}
  resource_additional_dimensions = {}

  alarm_thresholds = {
    root_zone = {
      "health-check-status-critical"             = var.route53_health_check_status_critical_alarm_threshold
      "health-check-percentage-healthy-critical" = var.route53_health_check_percentage_healthy_critical_alarm_threshold
    }
  }

  alarm_evaluation_periods = {
    root_zone = {
      "health-check-status-critical"             = var.route53_health_check_status_critical_alarm_evaluation_periods
      "health-check-percentage-healthy-critical" = var.route53_health_check_percentage_healthy_critical_alarm_evaluation_periods
    }
  }

  alarm_periods = {
    root_zone = {
      "health-check-status-critical"             = var.route53_health_check_status_critical_alarm_period
      "health-check-percentage-healthy-critical" = var.route53_health_check_percentage_healthy_critical_alarm_period
    }
  }

  slack_notifier_function_name = local.slack_notifier_function_name

  tags = {
    Name = "${local.resource_prefix}-route53-root-zone-alarms"
  }
}
