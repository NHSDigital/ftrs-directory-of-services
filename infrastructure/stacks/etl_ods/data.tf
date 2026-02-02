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
}

data "aws_subnet" "private_subnets_details" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}

data "aws_kms_key" "secrets_manager_kms_key" {
  key_id = local.kms_aliases.secrets_manager
}

data "aws_kms_key" "ssm_kms_key" {
  key_id = local.kms_aliases.ssm
}

data "aws_s3_object" "python_dependency_layer" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-${var.stack_name}-python-dependency-layer.zip"
}

data "aws_s3_object" "common_packages_layer" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
}

data "aws_s3_object" "extractor_lambda_package" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-${var.stack_name}-${var.extractor_name}.zip"
}

data "aws_s3_object" "transformer_lambda_package" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-${var.stack_name}-${var.transformer_name}.zip"
}

data "aws_s3_object" "consumer_lambda_package" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-${var.stack_name}-${var.consumer_name}.zip"
}

data "aws_iam_policy_document" "s3_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "${module.etl_ods_store_bucket.s3_bucket_arn}/",
      "${module.etl_ods_store_bucket.s3_bucket_arn}/*",
    ]
  }
}

data "aws_iam_policy_document" "sqs_access_policy" {
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:SendMessage",
      "sqs:GetQueueUrl"
    ]
    resources = [
      aws_sqs_queue.load_queue.arn,
      aws_sqs_queue.transform_queue.arn,
    ]
  }
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
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${local.project_prefix}-crud-apis${local.workspace_suffix}/endpoint"
    ]
  }
}

# TODO: FDOS-378 - This is overly permissive and should be resolved when we have control over stack deployment order.
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

data "aws_iam_policy_document" "secretsmanager_jwt_credentials_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:/${var.project}/${var.environment}/dos-ingest-jwt-credentials*",
      "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:/${var.project}/${var.environment}/ods-terminology-api-key*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = [
      data.aws_kms_key.secrets_manager_kms_key.arn
    ]
  }
}

data "aws_iam_policy_document" "ods_mock_api_access_policy" {
  count = var.environment == "dev" ? 1 : 0

  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:/${local.project_prefix}/mock-api/api-key${local.workspace_suffix}*"
    ]
  }
}


data "aws_iam_policy_document" "ods_etl_scheduler_invoke_policy" {
  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      module.extractor_lambda.lambda_function_arn
    ]
  }
}

data "aws_kms_key" "sqs_kms_alias" {
  key_id = local.kms_aliases.sqs
}

data "aws_iam_policy_document" "lambda_kms_access" {
  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*"
    ]
    resources = [data.aws_kms_key.sqs_kms_alias.arn]
  }
}

data "aws_security_group" "etl_ods_lambda_security_group" {
  count = local.is_primary_environment ? 0 : 1

  name = "${local.resource_prefix}-lambda-sg"
}
