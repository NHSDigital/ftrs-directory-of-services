data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }

  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc-private-*"]
  }

  filter {
    name   = "tag:CidrRange"
    values = [var.vpc_private_subnet_cidr_range]
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}

data "aws_s3_object" "common_packages_layer" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
}

data "aws_s3_object" "python_dependency_layer" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-${var.stack_name}-python-dependency-layer.zip"
}

data "aws_s3_object" "crud_apis_lambda_package" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-${var.stack_name}-lambda.zip"
}

data "aws_s3_object" "truststore" {
  bucket = local.s3_trust_store_bucket_name
  key    = local.trust_store_file_path
}

data "aws_iam_policy_document" "s3_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "${module.crud_apis_bucket.s3_bucket_arn}/",
      "${module.crud_apis_bucket.s3_bucket_arn}/*",
    ]
  }
}

data "aws_iam_policy_document" "dynamodb_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
      "dynamodb:Query"
    ]
    resources = flatten([
      for table in local.dynamodb_tables : [
        table.arn,
        "${table.arn}/index/*"
      ]
    ])
  }
}

data "aws_prefix_list" "dynamodb" {
  name = "com.amazonaws.${var.aws_region}.dynamodb"
}

data "aws_ssm_parameter" "appconfig_application_id" {
  name = "/${var.project}/${var.environment}/appconfig/application_id${local.workspace_suffix}"
}

data "aws_appconfig_configuration_profiles" "appconfig_configuration_profiles" {
  application_id = data.aws_ssm_parameter.appconfig_application_id.value
}

data "aws_appconfig_environments" "appconfig_environments" {
  application_id = data.aws_ssm_parameter.appconfig_application_id.value
}

data "aws_iam_policy" "appconfig_access_policy" {
  name = "${local.project_prefix}${local.workspace_suffix}-appconfig-data-read"
}

data "aws_security_group" "crud_apis_lambda_security_group" {
  count = local.is_primary_environment ? 0 : 1

  name = "${local.resource_prefix}-lambda-sg"
}

data "aws_kinesis_firehose_delivery_stream" "firehose_stream" {
  name = "${local.project_prefix}-${var.firehose_stack}-${var.firehose_name}"
}


data "aws_iam_role" "firehose_role" {
  name = "${local.account_prefix}-${var.firehose_name}-cw-role"
}
