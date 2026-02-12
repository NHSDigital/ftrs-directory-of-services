# Optional: Deploy Slack notifications using the slack_notifier stack as a module
# Set enable_slack_notifications = true to deploy

module "slack_notifier" {
  count  = var.enable_slack_notifications ? 1 : 0
  source = "../slack_notifier"

  sns_topic_arn     = module.lambda_monitoring.sns_topic_arn
  slack_webhook_url = var.slack_webhook_alarms_url

  vpc_name            = "${local.account_prefix}-vpc"
  security_group_ids  = [try(aws_security_group.dos_search_lambda_security_group[0].id, data.aws_security_group.dos_search_lambda_security_group[0].id)]
  lambda_artifact_key = "${local.artefact_base_path}/${var.project}-${var.stack_name}-lambda.zip"
  lambda_runtime      = var.lambda_runtime
  lambda_layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
  ]
  cloudwatch_logs_retention_days = var.lambda_cloudwatch_logs_retention_days
}
