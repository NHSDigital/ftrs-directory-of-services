data "aws_caller_identity" "current" {}

data "aws_kms_key" "secrets_manager_kms_key" {
  key_id = "alias/${local.account_prefix}-secrets-manager-kms-key"
}

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

data "aws_security_group" "processor_lambda_security_group" {
  count  = var.version_history_enabled ? 1 : 0
  vpc_id = data.aws_vpc.vpc.id

  filter {
    name   = "tag:Name"
    values = ["${local.resource_prefix}-processor-lambda-security-group"]
  }
}
