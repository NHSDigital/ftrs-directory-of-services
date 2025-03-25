module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 6.0"

  function_name           = "${var.function_name}${local.workspace_suffix}"
  handler                 = var.handler
  runtime                 = var.runtime
  publish                 = var.publish
  create_package          = var.create_package
  local_existing_package  = var.local_existing_package
  ignore_source_code_hash = var.ignore_source_code_hash
  attach_policy_jsons     = var.attach_policy_jsons
  number_of_policy_jsons  = var.number_of_policy_jsons
  description             = var.description
  policy_jsons            = var.policy_jsons
  timeout                 = var.timeout
  memory_size             = var.memory_size

  vpc_subnet_ids         = var.subnet_ids
  vpc_security_group_ids = var.security_group_ids

  environment_variables = merge(var.environment_variables, { WORKSPACE = "${local.environment_workspace}" })
  layers                = var.layers

  depends_on = [
    aws_cloudwatch_log_group.lambda_log_group
  ]
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention
}
