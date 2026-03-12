# Route 53 health check metrics are published to CloudWatch in us-east-1 only
# (AWS global service constraint). These alarms use provider = aws.us-east-1
# but send their actions to the eu-west-2 SNS topic (created by
# acm_api_cert_alarms) where the Slack Lambda subscription already exists.
# CloudWatch alarms natively support cross-region SNS targets.

resource "aws_cloudwatch_metric_alarm" "route53_health_check_status_critical_environment_zone" {
  count    = var.environment == "mgmt" ? 0 : 1
  provider = aws.us-east-1

  alarm_name          = "${local.resource_prefix}-environment-zone-health-check-status-critical"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.route53_health_check_status_critical_alarm_evaluation_periods
  metric_name         = "HealthCheckStatus"
  namespace           = "AWS/Route53"
  period              = var.route53_health_check_status_critical_alarm_period
  statistic           = "Minimum"
  threshold           = var.route53_health_check_status_critical_alarm_threshold
  alarm_description   = "Route 53 health check is unhealthy - DNS or domain availability issue detected for ${local.root_domain_name}"
  treat_missing_data  = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alarms.arn
  ]

  dimensions = {
    HealthCheckId = aws_route53_health_check.environment_zone[0].id
  }

  tags = {
    Name = "${local.resource_prefix}-environment-zone-health-check-status-critical"
  }
}

resource "aws_cloudwatch_metric_alarm" "route53_health_check_percentage_healthy_critical_environment_zone" {
  count    = var.environment == "mgmt" ? 0 : 1
  provider = aws.us-east-1

  alarm_name          = "${local.resource_prefix}-environment-zone-health-check-percentage-healthy-critical"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.route53_health_check_percentage_healthy_critical_alarm_evaluation_periods
  metric_name         = "HealthCheckPercentageHealthy"
  namespace           = "AWS/Route53"
  period              = var.route53_health_check_percentage_healthy_critical_alarm_period
  statistic           = "Minimum"
  threshold           = var.route53_health_check_percentage_healthy_critical_alarm_threshold
  alarm_description   = "Route 53 health check percentage healthy is critically low for ${local.root_domain_name}"
  treat_missing_data  = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alarms.arn
  ]

  dimensions = {
    HealthCheckId = aws_route53_health_check.environment_zone[0].id
  }

  tags = {
    Name = "${local.resource_prefix}-environment-zone-health-check-percentage-healthy-critical"
  }
}

resource "aws_cloudwatch_metric_alarm" "route53_health_check_status_critical_root_zone" {
  count    = var.environment == "mgmt" ? 1 : 0
  provider = aws.us-east-1

  alarm_name          = "${local.resource_prefix}-root-zone-health-check-status-critical"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.route53_health_check_status_critical_alarm_evaluation_periods
  metric_name         = "HealthCheckStatus"
  namespace           = "AWS/Route53"
  period              = var.route53_health_check_status_critical_alarm_period
  statistic           = "Minimum"
  threshold           = var.route53_health_check_status_critical_alarm_threshold
  alarm_description   = "Route 53 health check is unhealthy - DNS or domain availability issue detected for ${local.root_domain_name}"
  treat_missing_data  = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alarms.arn
  ]

  dimensions = {
    HealthCheckId = aws_route53_health_check.root_zone[0].id
  }

  tags = {
    Name = "${local.resource_prefix}-root-zone-health-check-status-critical"
  }
}

resource "aws_cloudwatch_metric_alarm" "route53_health_check_percentage_healthy_critical_root_zone" {
  count    = var.environment == "mgmt" ? 1 : 0
  provider = aws.us-east-1

  alarm_name          = "${local.resource_prefix}-root-zone-health-check-percentage-healthy-critical"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = var.route53_health_check_percentage_healthy_critical_alarm_evaluation_periods
  metric_name         = "HealthCheckPercentageHealthy"
  namespace           = "AWS/Route53"
  period              = var.route53_health_check_percentage_healthy_critical_alarm_period
  statistic           = "Minimum"
  threshold           = var.route53_health_check_percentage_healthy_critical_alarm_threshold
  alarm_description   = "Route 53 health check percentage healthy is critically low for ${local.root_domain_name}"
  treat_missing_data  = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alarms.arn
  ]

  dimensions = {
    HealthCheckId = aws_route53_health_check.root_zone[0].id
  }

  tags = {
    Name = "${local.resource_prefix}-root-zone-health-check-percentage-healthy-critical"
  }
}
