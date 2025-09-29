# SNS Topic for Shield DDoS alerts
#trivy:ignore:AVD-AWS-0136
resource "aws_sns_topic" "shield_ddos_alerts" {
  #checkov:skip=CKV_AWS_26: Revisit with the encryption work
  name = "${var.resource_prefix}-shield-ddos-alerts"

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
