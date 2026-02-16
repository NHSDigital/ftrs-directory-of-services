resource "aws_lambda_layer_version" "common_packages_layer" {
  layer_name          = "${local.resource_prefix}-common-packages-layer${local.workspace_suffix}"
  compatible_runtimes = [var.organisation_api_lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
  s3_object_version = data.aws_s3_object.common_packages_layer.version_id
}

resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.organisation_api_lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-${var.stack_name}-python-dependency-layer.zip"
  s3_object_version = data.aws_s3_object.python_dependency_layer.version_id
}

module "organisation_api_lambda" {
  # checkov:skip=CKV_AWS_111: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-421
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.organisation_api_lambda_name}"
  description             = "Lambda to expose CRUD apis for organisations"
  handler                 = var.organisation_api_lambda_handler
  runtime                 = var.organisation_api_lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${local.artefact_base_path}/${var.project}-${var.stack_name}-lambda.zip"
  ignore_source_code_hash = false
  s3_key_version_id       = data.aws_s3_object.crud_apis_lambda_package.version_id
  timeout                 = var.organisation_api_lambda_timeout
  memory_size             = var.organisation_api_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [try(aws_security_group.crud_apis_lambda_security_group[0].id, data.aws_security_group.crud_apis_lambda_security_group[0].id)]

  number_of_policy_jsons = "3"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.dynamodb_access_policy.json,
    data.aws_iam_policy.appconfig_access_policy.policy,
  ]
  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
    local.appconfig_lambda_extension_layer_arn,
  ]

  environment_variables = {
    "ENVIRONMENT"                        = var.environment
    "WORKSPACE"                          = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME"                       = var.project
    "APPCONFIG_APPLICATION_ID"           = data.aws_ssm_parameter.appconfig_application_id.value
    "APPCONFIG_ENVIRONMENT_ID"           = local.appconfig_environment_id
    "APPCONFIG_CONFIGURATION_PROFILE_ID" = local.appconfig_configuration_profile_id
  }

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${module.api_gateway.api_execution_arn}/*/*"
    }
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.crud_api_lambda_logs_retention

  build_splunk_subscription = var.build_splunk_subscription
  firehose_role_arn         = data.aws_iam_role.firehose_role.arn
  firehose_arn              = data.aws_kinesis_firehose_delivery_stream.firehose_stream.arn
}

module "healthcare_service_api_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.healthcare_service_api_lambda_name}"
  description             = "Lambda to expose CRUD apis for healthcare services"
  handler                 = var.healthcare_service_api_lambda_handler
  runtime                 = var.healthcare_service_api_lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${local.artefact_base_path}/${var.project}-${var.stack_name}-lambda.zip"
  ignore_source_code_hash = false
  s3_key_version_id       = data.aws_s3_object.crud_apis_lambda_package.version_id
  timeout                 = var.healthcare_service_api_lambda_timeout
  memory_size             = var.healthcare_service_api_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [try(aws_security_group.crud_apis_lambda_security_group[0].id, data.aws_security_group.crud_apis_lambda_security_group[0].id)]

  number_of_policy_jsons = "3"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.dynamodb_access_policy.json,
    data.aws_iam_policy.appconfig_access_policy.policy,
  ]
  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
    local.appconfig_lambda_extension_layer_arn,
  ]

  environment_variables = {
    "ENVIRONMENT"                        = var.environment
    "WORKSPACE"                          = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME"                       = var.project
    "APPCONFIG_APPLICATION_ID"           = data.aws_ssm_parameter.appconfig_application_id.value
    "APPCONFIG_ENVIRONMENT_ID"           = local.appconfig_environment_id
    "APPCONFIG_CONFIGURATION_PROFILE_ID" = local.appconfig_configuration_profile_id
  }

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${module.api_gateway.api_execution_arn}/*/*"
    }
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.crud_api_lambda_logs_retention

  build_splunk_subscription = var.build_splunk_subscription
  firehose_role_arn         = data.aws_iam_role.firehose_role.arn
  firehose_arn              = data.aws_kinesis_firehose_delivery_stream.firehose_stream.arn
}

module "location_api_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.resource_prefix}-${var.location_api_lambda_name}"
  description             = "Lambda to expose CRUD apis for locations"
  handler                 = var.location_api_lambda_handler
  runtime                 = var.location_api_lambda_runtime
  s3_bucket_name          = local.artefacts_bucket
  s3_key                  = "${local.artefact_base_path}/${var.project}-${var.stack_name}-lambda.zip"
  ignore_source_code_hash = false
  s3_key_version_id       = data.aws_s3_object.crud_apis_lambda_package.version_id
  timeout                 = var.location_api_lambda_timeout
  memory_size             = var.location_api_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [try(aws_security_group.crud_apis_lambda_security_group[0].id, data.aws_security_group.crud_apis_lambda_security_group[0].id)]

  number_of_policy_jsons = "3"
  policy_jsons = [
    data.aws_iam_policy_document.s3_access_policy.json,
    data.aws_iam_policy_document.dynamodb_access_policy.json,
    data.aws_iam_policy.appconfig_access_policy.policy,
  ]
  layers = [
    aws_lambda_layer_version.python_dependency_layer.arn,
    aws_lambda_layer_version.common_packages_layer.arn,
    local.appconfig_lambda_extension_layer_arn,
  ]

  environment_variables = {
    "ENVIRONMENT"                        = var.environment
    "WORKSPACE"                          = terraform.workspace == "default" ? "" : terraform.workspace
    "PROJECT_NAME"                       = var.project
    "APPCONFIG_APPLICATION_ID"           = data.aws_ssm_parameter.appconfig_application_id.value
    "APPCONFIG_ENVIRONMENT_ID"           = local.appconfig_environment_id
    "APPCONFIG_CONFIGURATION_PROFILE_ID" = local.appconfig_configuration_profile_id
  }

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${module.api_gateway.api_execution_arn}/*/*"
    }
  }
  account_id     = data.aws_caller_identity.current.account_id
  account_prefix = local.account_prefix
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.vpc.id

  cloudwatch_logs_retention = var.crud_api_lambda_logs_retention

  build_splunk_subscription = var.build_splunk_subscription
  firehose_role_arn         = data.aws_iam_role.firehose_role.arn
  firehose_arn              = data.aws_kinesis_firehose_delivery_stream.firehose_stream.arn
}
