module "health_check_lambda" {
  source                 = "github.com/NHSDigital/ftrs-directory-of-services?ref=ebe96e5/infrastructure/modules/lambda"
  function_name          = "${local.resource_prefix}-${var.health_check_lambda_name}"
  description            = "This lambda provides a health check for the search lambda"
  handler                = "health_check/health_check_function.lambda_handler"
  runtime                = var.lambda_runtime
  s3_bucket_name         = local.artefacts_bucket
  s3_key                 = "${terraform.workspace}/${var.commit_hash}/${var.gp_search_service_name}-lambda-${var.application_tag}.zip"
  attach_tracing_policy  = true
  tracing_mode           = "Active"
  number_of_policy_jsons = "2"
  policy_jsons           = [data.aws_iam_policy_document.vpc_access_policy.json, data.aws_iam_policy_document.dynamodb_access_policy.json]
  timeout                = var.lambda_timeout
  memory_size            = var.lambda_memory_size

  layers = (
    [aws_lambda_layer_version.python_dependency_layer.arn]
  )

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.gp_search_lambda_security_group.id]

  environment_variables = {
    "ENVIRONMENT"         = var.environment
    "PROJECT_NAME"        = var.project
    "NAMESPACE"           = "${var.gp_search_service_name}${local.workspace_suffix}"
    "DYNAMODB_TABLE_NAME" = var.dynamodb_organisation_table_name
  }
}
