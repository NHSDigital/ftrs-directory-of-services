data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_ec2_client_vpn_endpoint" "client_vpn_endpoint" {
  count = var.environment == "dev" ? 1 : 0
  filter {
    name   = "tag:Project"
    values = ["${var.project}"]
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
