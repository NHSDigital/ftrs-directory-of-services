module "frontend_lambda" {
  count  = local.stack_enabled
  source = "../../modules/lambda"

  description   = "Read only viewer frontend server lambda"
  function_name = "${local.resource_prefix}-${var.frontend_lambda_name}"
  runtime       = var.frontend_lambda_runtime
  handler       = "index.handler"

  s3_bucket_name = local.artefacts_bucket
  s3_key         = "${local.artefact_base_path}/read-only-viewer-server.zip"

  ignore_source_code_hash = false
  s3_key_version_id       = data.aws_s3_object.read_only_viewer_lambda_package[0].version_id
  timeout                 = var.frontend_lambda_connection_timeout
  memory_size             = var.frontend_lambda_memory_size

  number_of_policy_jsons = "2"
  policy_jsons = [
    data.aws_iam_policy_document.ssm_access_policy[0].json,
    data.aws_iam_policy_document.execute_api_policy[0].json
  ]

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.frontend_lambda_security_group[0].id]
  layers             = []

  environment_variables = {
    "ENVIRONMENT" = var.environment
    "WORKSPACE"   = terraform.workspace == "default" ? "" : terraform.workspace
  }

  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc[0].id
}

resource "aws_lambda_function_url" "frontend_lambda_url" {
  count = local.stack_enabled
  # checkov:skip=CKV_AWS_258: Justification: This Lambda function URL is only accessible via CloudFront, which enforces authentication and access controls.
  function_name      = module.frontend_lambda[0].lambda_function_name
  authorization_type = "NONE"
}
