data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${var.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }

  filter {
    name   = "tag:Name"
    values = ["${var.account_prefix}-vpc-private-*"]
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
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


data "aws_iam_policy_document" "allow_private_subnet_policy" {
  statement {
    sid    = "AllowPrivateSubnetAccess"
    effect = "Allow"
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
