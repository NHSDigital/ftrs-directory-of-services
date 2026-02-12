module "slack_notifications" {
  source = "../../modules/slack-notifications"

  resource_prefix = local.resource_prefix_slack
  sns_topic_arn   = var.sns_topic_arn

  slack_webhook_url = var.slack_webhook_url
  environment       = var.environment
  project_name      = var.project
  workspace         = terraform.workspace == "default" ? "" : terraform.workspace

  lambda_s3_bucket = local.artefacts_bucket
  lambda_s3_key    = local.lambda_s3_key

  lambda_runtime     = var.lambda_runtime
  lambda_timeout     = var.lambda_timeout
  lambda_memory_size = var.lambda_memory_size

  lambda_layers = var.lambda_layers

  subnet_ids         = data.aws_subnets.private.ids
  security_group_ids = var.security_group_ids

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention_days = var.cloudwatch_logs_retention_days
  enable_xray_tracing            = var.enable_xray_tracing
}
