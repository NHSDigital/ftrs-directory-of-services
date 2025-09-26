# SNS Topic for Shield DDoS alerts
resource "aws_sns_topic" "shield_ddos_alerts" {
  name              = "${var.resource_prefix}-shield-ddos-alerts"
  kms_master_key_id = "alias/aws/sns"

  tags = {
    Name = "${var.resource_prefix}-shield-ddos-alerts"
  }
}

# Email subscription for the SNS topic - one subscription for each email address
resource "aws_sns_topic_subscription" "shield_ddos_email_subscription" {
  for_each  = toset(var.alarm_notification_email)
  topic_arn = aws_sns_topic.shield_ddos_alerts.arn
  protocol  = "email"
  endpoint  = each.value
}
