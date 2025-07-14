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
      variable = "lambda:SourceFunctionArn"
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
      test     = "ForAnyValue:StringEquals"
      variable = "lambda:SubnetIds"
      values   = var.subnet_ids

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
      values   = [var.vpc_id]

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
