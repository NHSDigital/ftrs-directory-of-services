data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  count = var.version_history_enabled ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }

  tags = {
    Tier = "Private"
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = var.version_history_enabled ? toset(data.aws_subnets.private_subnets[0].ids) : []
  id       = each.value
}
