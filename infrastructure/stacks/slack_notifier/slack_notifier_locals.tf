locals {
  stack_enabled         = var.slack_notifier_stack_enabled ? 1 : 0
  vpc_endpoints_enabled = var.slack_notifier_stack_enabled && var.enable_vpc_endpoints ? 1 : 0
  sns_topic_name        = "${local.resource_prefix}-alarms"
  lambda_s3_key         = "${local.artefact_base_path}/${var.project}-slack-notifier-lambda.zip"
}
