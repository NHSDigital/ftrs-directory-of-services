module "sandbox_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.sandbox_lambda_name}"
  description             = "Lambda to return sandbox responses"
  handler                 = var.sandbox_lambda_handler
  runtime                 = var.sandbox_lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${terraform.workspace}/${var.commit_hash}/${var.project}-${var.stack_name}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.sandbox_lambda_timeout
  memory_size             = var.sandbox_lambda_memory_size
  # create                  = var.environment == "sandbox"

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.sandbox_lambda_security_group.id]

  number_of_policy_jsons = "1"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
  ]
  layers = []

  environment_variables = {
    "ENVIRONMENT"  = var.environment
    "WORKSPACE"    = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME" = var.project
  }

  # allowed_triggers = {
  #   AllowExecutionFromAPIGateway = {
  #     service    = "apigateway"
  #     source_arn = "${module.api_gateway.api_execution_arn}/*/*"
  #   }
  # }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id
}

resource "aws_ssm_parameter" "sandbox_lambda_function_arn" {
  # checkov:skip=CKV2_AWS_34: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-402
  name        = "/${local.resource_prefix}/sandbox-lambda/function-arn"
  description = "The function ARN for the sandbox Lambda"
  type        = "String"
  value       = module.sandbox_lambda.lambda_function_arn
}

resource "aws_ssm_parameter" "sandbox_lambda_function_name" {
  # checkov:skip=CKV2_AWS_34: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-402
  name        = "/${local.resource_prefix}/sandbox-lambda/function-name"
  description = "The function name for the sandbox Lambda"
  type        = "String"
  value       = module.sandbox_lambda.lambda_function_name
}
