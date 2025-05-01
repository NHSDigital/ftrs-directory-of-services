module "frontend_lambda" {
  source = "../../modules/lambda"

  description   = "Read only viewer frontend server lambda"
  function_name = "${local.resource_prefix}-${var.frontend_lambda_name}"
  runtime       = "nodejs20.x"
  handler       = "index.handler"

  s3_bucket_name = local.artefacts_bucket
  s3_key         = "${terraform.workspace}/${var.commit_hash}/read-only-viewer-server-latest.zip"

  ignore_source_code_hash = false
  timeout                 = var.frontend_lambda_connection_timeout
  memory_size             = var.frontend_lambda_memory_size
  publish                 = true
  lambda_at_edge          = true

  number_of_policy_jsons = "0"
  policy_jsons           = []
  security_group_ids     = null
  subnet_ids             = null
  layers                 = []
  environment_variables  = {}
}
