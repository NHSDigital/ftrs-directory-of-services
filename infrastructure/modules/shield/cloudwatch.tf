# CloudWatch Metric Alarm to monitor DDoS events for each protected resource
resource "aws_cloudwatch_metric_alarm" "shield_advanced_cloudwatch_metric" {
  for_each            = var.arns_to_protect
  alarm_name          = "${var.resource_prefix}-shield-ddos-alarm-${each.key}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.evaluation_period
  metric_name         = "DDoSDetected"
  namespace           = "AWS/DDoSProtection"
  period              = "60"
  statistic           = "Maximum"
  threshold           = "0"
  treat_missing_data  = "notBreaching"
  alarm_description   = "Whenever DDoSDetected is - Greater than 0"
  alarm_actions       = [aws_sns_topic.shield_ddos_alerts.arn]

  dimensions = {
    ResourceArn = each.value
  }
}
