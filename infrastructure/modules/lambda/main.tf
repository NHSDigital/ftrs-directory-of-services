#trivy:ignore:AVD-AWS-0066
module "lambda" {
  # Module version: 8.1.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=1c3b16a8d9ee8944ba33f5327bdf011c6639cceb"

  function_name          = "${var.function_name}${local.workspace_suffix}"
  handler                = var.handler
  runtime                = var.runtime
  publish                = var.publish
  attach_policy_jsons    = var.attach_policy_jsons
  number_of_policy_jsons = length(local.additional_json_policies)
  attach_tracing_policy  = var.attach_tracing_policy
  tracing_mode           = var.tracing_mode
  description            = var.description
  policy_jsons           = local.additional_json_policies
  timeout                = var.timeout
  memory_size            = var.memory_size

  create_package          = var.s3_bucket_name == "" ? var.create_package : false
  local_existing_package  = var.s3_bucket_name == "" ? var.local_existing_package : null
  ignore_source_code_hash = var.ignore_source_code_hash
  allowed_triggers        = var.allowed_triggers

  s3_existing_package = var.s3_bucket_name != "" ? {
    bucket = var.s3_bucket_name
    # Prefer an explicit key if provided. Otherwise, allow stacks to pass a base prefix in `s3_key`
    # and a per-lambda `lambda_name` to get granular artefact naming.
    key = (
      var.s3_key != "" ? var.s3_key : (
        var.lambda_name != "" ? "${var.lambda_name}.zip" : ""
      )
    )
  } : null

  vpc_subnet_ids         = var.subnet_ids
  vpc_security_group_ids = var.security_group_ids

  environment_variables = merge(var.environment_variables, { WORKSPACE = "${local.environment_workspace}" })
  layers                = var.layers

  cloudwatch_logs_retention_in_days = var.cloudwatch_logs_retention
  logging_system_log_level          = var.cloudwatch_log_level
}
