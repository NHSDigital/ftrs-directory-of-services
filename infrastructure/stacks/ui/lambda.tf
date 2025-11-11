module "ui_lambda" {
  source = "../../modules/lambda"

  description   = "UI frontend server lambda"
  function_name = "${local.resource_prefix}-${var.ui_lambda_name}"
  runtime       = var.ui_lambda_runtime
  handler       = "index.handler"

  s3_bucket_name = local.artefacts_bucket
  s3_key         = "${local.artefact_base_path}/dos-ui-server-${var.application_tag}.zip"

  ignore_source_code_hash = false
  timeout                 = var.ui_lambda_connection_timeout
  memory_size             = var.ui_lambda_memory_size

  number_of_policy_jsons = "4"

  policy_jsons = [
    data.aws_iam_policy_document.ssm_access_policy.json,
    data.aws_iam_policy_document.execute_api_policy.json,
    data.aws_iam_policy_document.dynamodb_session_store_policy.json,
    data.aws_iam_policy_document.secretsmanager_cis2_credentials_access_policy.json
  ]

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.ui_lambda_security_group.id]
  layers             = []

  environment_variables = {
    "ENVIRONMENT"         = var.environment
    "PROJECT"             = var.project
    "WORKSPACE"           = terraform.workspace == "default" ? "" : terraform.workspace
    "SESSION_STORE_TABLE" = "${local.resource_prefix}-session-store${local.workspace_suffix}"
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id
}

resource "aws_lambda_function_url" "ui_lambda_url" {
  # checkov:skip=CKV_AWS_258: Justification: This Lambda function URL is only accessible via CloudFront, which enforces authentication and access controls.
  function_name      = module.ui_lambda.lambda_function_name
  authorization_type = "NONE"
}
