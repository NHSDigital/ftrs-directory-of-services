resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket        = local.artefacts_bucket
  s3_key           = "${var.project}-python-dependency-layer/${var.project}-python-dependency-layer-${var.application_tag}.zip"
  source_code_hash = data.aws_s3_object.python_dependency_layer.checksum_sha256
}

data "aws_s3_object" "python_dependency_layer" {
  bucket = local.artefacts_bucket
  key    = "${var.project}-python-dependency-layer/${var.project}-python-dependency-layer-${var.application_tag}.zip"
}

module "extract_lambda" {
  source                  = "../../modules/lambda"
  function_name           = "${local.prefix}-${var.extract_name}${local.workspace_suffix}"
  description             = "Lambda to extract data for the DoS mirgration"
  handler                 = var.extract_lambda_handler
  runtime                 = var.lambda_runtime
  local_existing_package  = "${path.module}/${var.project}-lambda-${var.application_tag}.zip"
  ignore_source_code_hash = false
  timeout                 = var.extract_lambda_connection_timeout
  memory_size             = var.extract_lambda_memory_size

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.extract_lambda_security_group.id]

  number_of_policy_jsons = "2"
  policy_jsons           = [data.aws_iam_policy_document.s3_access_policy.json, data.aws_iam_policy_document.vpc_access_policy.json]

  layers = [aws_lambda_layer_version.python_dependency_layer.arn]
}

data "aws_iam_policy_document" "s3_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "*"
    ]
  }
}

data "aws_iam_policy_document" "vpc_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
    ]
    resources = [
      "*"
    ]
  }
}
