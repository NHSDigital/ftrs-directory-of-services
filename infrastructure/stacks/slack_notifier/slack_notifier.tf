# SNS Topic for CloudWatch Alarms
resource "aws_sns_topic" "slack_notifications" {
  name              = local.sns_topic_name
  display_name      = "Slack Notifications for ${var.environment}"
  kms_master_key_id = data.aws_kms_key.sns.id

  tags = {
    Name = local.sns_topic_name
  }
}

module "slack_notifications" {
  source = "../../modules/slack-notifications"

  resource_prefix = local.resource_prefix
  sns_topic_arn   = aws_sns_topic.slack_notifications.arn

  slack_webhook_url = var.slack_webhook_alarms_url
  environment       = var.environment
  project_name      = var.project
  workspace         = terraform.workspace == "default" ? "" : terraform.workspace

  lambda_s3_bucket = local.artefacts_bucket
  lambda_s3_key    = local.lambda_s3_key

  lambda_runtime     = var.lambda_runtime
  lambda_timeout     = 30
  lambda_memory_size = 128

  lambda_layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]

  subnet_ids         = data.aws_subnets.private.ids
  security_group_ids = local.is_primary_environment ? [aws_security_group.slack_notifier_lambda_sg[0].id] : [data.aws_security_group.slack_notifier_lambda_sg_existing[0].id]

  account_id     = local.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention_days = 7
  enable_xray_tracing            = true
}
