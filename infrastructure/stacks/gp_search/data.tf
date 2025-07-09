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

data "aws_dynamodb_table" "dynamodb_organisation_table" {
  name = var.dynamodb_organisation_table_name
}

data "aws_route53_zone" "dev_ftrs_cloud" {
  name         = local.root_domain_name
  private_zone = false
}

data "aws_acm_certificate" "domain_cert" {
  domain      = "*.${local.root_domain_name}"
  statuses    = ["ISSUED"]
  most_recent = true
}
