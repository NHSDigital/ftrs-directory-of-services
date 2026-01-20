data "aws_vpc" "vpc" {
  count = local.stack_enabled
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  count = local.stack_enabled
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc[0].id]
  }

  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc-private-*"]
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = local.stack_enabled == 1 ? toset(data.aws_subnets.private_subnets[0].ids) : []
  id       = each.value
}

data "aws_opensearchserverless_collection" "opensearch_serverless_collection" {
  count = local.stack_enabled
  name  = "${local.project_prefix}-osc"
}

data "aws_opensearchserverless_security_policy" "opensearch_serverless_network_access_policy" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 0 : 1
  name  = "${var.environment}-${var.stack_name}-nap"
  type  = "network"
}
