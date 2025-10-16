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

data "aws_opensearchserverless_collection" "opensearch_serverless_collection" {
  name = "${var.project}-${var.environment}-osc"
}

data "aws_opensearchserverless_security_policy" "opensearch_serverless_network_access_policy" {
  count = local.is_primary_environment ? 0 : 1
  name  = "${var.environment}-${var.stack_name}-nap"
  type  = "network"
}
