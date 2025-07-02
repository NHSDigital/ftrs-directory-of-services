module "lambda" {
  # Module version: 7.21.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=f1f06ed88f567ec75815bd37897d612092e7941c"

  function_name       = "${var.function_name}${local.workspace_suffix}"
  handler             = var.handler
  runtime             = var.runtime
  publish             = var.publish
  attach_policy_jsons = var.attach_policy_jsons
  # number_of_policy_jsons = var.number_of_policy_jsons
  number_of_policy_jsons = length(local.additional_json_policies)
  attach_tracing_policy  = var.attach_tracing_policy
  tracing_mode           = var.tracing_mode
  description            = var.description
  # policy_jsons           = var.policy_jsons
  policy_jsons = local.additional_json_policies
  timeout      = var.timeout
  memory_size  = var.memory_size

  create_package          = var.s3_bucket_name == "" ? var.create_package : false
  local_existing_package  = var.s3_bucket_name == "" ? var.local_existing_package : null
  ignore_source_code_hash = var.ignore_source_code_hash
  allowed_triggers        = var.allowed_triggers

  s3_existing_package = var.s3_bucket_name != "" ? {
    bucket = var.s3_bucket_name
    key    = var.s3_key
  } : null

  vpc_subnet_ids         = var.subnet_ids
  vpc_security_group_ids = var.security_group_ids

  environment_variables = merge(var.environment_variables, { WORKSPACE = "${local.environment_workspace}" })
  layers                = var.layers
}

data "aws_iam_policy_document" "vpc_access_policy" {
  statement {
    sid    = "AllowVpcAccess"
    effect = "Allow"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeSubnets",
      "ec2:AssignPrivateIpAddresses",
      "ec2:UnassignPrivateIpAddresses"
    ]
    resources = [
      "*"
    ]
    condition {
      test     = "StringEquals"
      variable = "lambda:VpcIds"
      values   = [data.aws_vpc.vpc.id]

    }
  }
}

data "aws_iam_policy_document" "deny_lambda_function_access_policy" {
  statement {
    sid    = "DenyLambdaFunctionAccess"
    effect = "Deny"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DeleteNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeSubnets",
      "ec2:DetachNetworkInterface",
      "ec2:AssignPrivateIpAddresses",
      "ec2:UnassignPrivateIpAddresses"
    ]
    resources = ["*"]
    condition {
      test     = "ArnEquals"
      variable = "lambda:FunctionArn"
      values = [
        "arn:aws:lambda:${var.aws_region}:${var.account_id}:function:${var.function_name}${local.workspace_suffix}"

      ]
    }
  }
}


data "aws_iam_policy_document" "deny_non_private_subnet_policy" {

  statement {
    sid    = "DenyNonPrivateSubnetAccess"
    effect = "Deny"
    actions = [
      "lambda:CreateFunction",
      "lambda:UpdateFunctionConfiguration"
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "lambda:SubnetIds"
      values   = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]

    }
  }
}


data "aws_iam_policy_document" "limit_to_environment_vpc_policy" {

  statement {
    sid    = "EnforceStayInSpecificVpc"
    effect = "Allow"
    actions = [
      "lambda:CreateFunction",
      "lambda:UpdateFunctionConfiguration"
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "lambda:VpcIds"
      values   = [data.aws_vpc.vpc.id]

    }
  }
}

data "aws_iam_policy_document" "enforce_vpc_lambda_policy" {

  statement {
    sid    = "EnforceVpcFunction"
    effect = "Deny"
    actions = [
      "lambda:CreateFunction",
      "lambda:UpdateFunctionConfiguration"
    ]
    resources = ["*"]
    condition {
      test     = "Null"
      variable = "lambda:VpcIds"
      values   = ["true"]

    }
  }
}


output "lambda_function_arn" {
  value = module.lambda.lambda_function_arn
}

output "lambda_function_name" {
  value = module.lambda.lambda_function_name
}

output "lambda_role_arn" {
  value = module.lambda.lambda_role_arn
}
