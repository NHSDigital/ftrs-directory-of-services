module "sns" {
  source = "../../modules/sns"

  topic_name   = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}" #TODO: make it environment specific
  display_name = "DoS Search Lambda Alarms"
  kms_key_id   = null # TODO Add KMS Key ID if needed for encryption

  subscriptions = {
    slack_lambda = {
      protocol = "lambda"
      endpoint = module.slack_notification_lambda.lambda_function_arn
    }
  }

  tags = {
    Name = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  }
}
