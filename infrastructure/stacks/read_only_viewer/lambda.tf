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
  security_group_ids    = null
  subnet_ids            = null
  layers                = []
  environment_variables = {}
}

data "aws_iam_policy_document" "ssm_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/ftrs-dos-${var.environment}-crud-apis${local.workspace_suffix}/endpoint"
    ]
  }
}

# TODO: This is overly permissive and should be resolved when we have control over stack deployment order.
data "aws_iam_policy_document" "execute_api_policy" {
  statement {
    effect = "Allow"
    actions = [
      "execute-api:Invoke"
    ]
    resources = [
      "arn:aws:execute-api:*:*:*/*/*/*/*"
    ]
  }
}

resource "aws_lambda_function_url" "frontend_lambda_url" {
  function_name      = module.frontend_lambda.lambda_name
  authorization_type = "NONE"
}
