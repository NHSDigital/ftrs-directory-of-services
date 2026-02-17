# SNS Topic for CloudWatch Alarms
module "sns_topic" {
  count  = local.stack_enabled
  source = "../../modules/sns"

  topic_name    = local.sns_topic_name
  display_name  = "Slack Notifications for ${var.environment}"
  kms_key_id    = data.aws_kms_key.sns[0].id
  subscriptions = {}

  tags = {
    Name = local.sns_topic_name
  }
}
