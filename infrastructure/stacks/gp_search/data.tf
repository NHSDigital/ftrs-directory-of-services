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

data "aws_route53_zone" "dev_ftrs_cloud" {
  name         = local.env_domain_name
  private_zone = false
}
data "aws_acm_certificate" "domain_cert" {
  domain      = "*.${local.env_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}

data "aws_iam_policy_document" "vpc_access_policy" {
  # checkov:skip=CKV_AWS_111: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-421
  # checkov:skip=CKV_AWS_356: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-421
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

data "aws_iam_policy_document" "dynamodb_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
    ]
    resources = flatten([
      for table in local.dynamodb_tables : [
        table.arn,
        "${table.arn}/index/*",
      ]
    ])
  }
}

data "aws_prefix_list" "dynamodb" {
  name = "com.amazonaws.${var.aws_region}.dynamodb"
}
