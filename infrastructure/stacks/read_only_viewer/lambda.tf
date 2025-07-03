module "frontend_lambda" {
  source = "../../modules/lambda"

  description   = "Read only viewer frontend server lambda"
  function_name = "${local.resource_prefix}-${var.frontend_lambda_name}"
  runtime       = var.frontend_lambda_runtime
  handler       = "index.handler"

  s3_bucket_name = local.artefacts_bucket
  s3_key         = "${terraform.workspace}/${var.commit_hash}/read-only-viewer-server-latest.zip"

  ignore_source_code_hash = false
  timeout                 = var.frontend_lambda_connection_timeout
  memory_size             = var.frontend_lambda_memory_size

  number_of_policy_jsons = "2"
  policy_jsons = [
    data.aws_iam_policy_document.ssm_access_policy.json,
    data.aws_iam_policy_document.execute_api_policy.json
  ]
  security_group_ids = null
  subnet_ids         = null
  layers             = []
  environment_variables = {
    "ENVIRONMENT" = var.environment
    "WORKSPACE"   = terraform.workspace == "default" ? "" : terraform.workspace
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
}

resource "aws_lambda_function_url" "frontend_lambda_url" {
  function_name      = module.frontend_lambda.lambda_function_name
  authorization_type = "NONE"
}
