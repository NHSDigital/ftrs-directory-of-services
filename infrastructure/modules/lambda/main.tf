module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 6.0"

  function_name          = "${var.function_name}${local.workspace_suffix}"
  handler                = var.handler
  runtime                = var.runtime
  publish                = var.publish
  attach_policy_jsons    = var.attach_policy_jsons
  number_of_policy_jsons = var.number_of_policy_jsons
  attach_tracing_policy  = var.attach_tracing_policy
  tracing_mode           = var.tracing_mode
  description            = var.description
  policy_jsons           = var.policy_jsons
  timeout                = var.timeout
  memory_size            = var.memory_size

  create_package          = var.s3_bucket_name == "" ? var.create_package : false
  local_existing_package  = var.s3_bucket_name == "" ? var.local_existing_package : null
  ignore_source_code_hash = var.ignore_source_code_hash

  s3_existing_package = var.s3_bucket_name != "" ? {
    bucket = var.s3_bucket_name
    key    = var.s3_key
  } : null

  vpc_subnet_ids         = var.subnet_ids
  vpc_security_group_ids = var.security_group_ids

  environment_variables = merge(var.environment_variables, { WORKSPACE = "${local.environment_workspace}" })
  layers                = var.layers
}
