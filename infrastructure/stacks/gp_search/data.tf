data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${var.main_project}-${var.environment}-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }

  filter {
    name   = "tag:Name"
    values = ["${var.main_project}-${var.environment}-vpc-private-*"]
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}

data "aws_security_group" "rds_security_group" {
  name = "${var.project}-${var.environment}-data-migration-rds-sg"
}
