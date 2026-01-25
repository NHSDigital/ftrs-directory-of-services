module "sns" {
  source = "../../modules/sns"

  topic_name   = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  display_name = "DoS Search Lambda Alarms"
  kms_key_id   = local.kms_aliases.sqs

  tags = {
    Name = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  }
}

module "appconfig_alarms" {
  source = "./appconfig_alarms"

  sns_topic_arn                     = module.sns.topic_arn
  search_lambda_function_name       = module.lambda.lambda_function_name
  health_check_lambda_function_name = module.health_check_lambda.lambda_function_name
  environment                       = var.environment

  tags = {
    Name = "${local.resource_prefix}-appconfig-alarms${local.workspace_suffix}"
  }
}
