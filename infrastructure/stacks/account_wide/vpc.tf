module "vpc" {
  # Module version: 5.21.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=7c1f791efd61f326ed6102d564d1a65d1eceedf0"

  name               = "${local.account_prefix}-${var.vpc["name"]}"
  cidr               = var.vpc["cidr"]
  enable_nat_gateway = var.enable_nat_gateway
  single_nat_gateway = var.single_nat_gateway

  create_database_subnet_group       = var.create_database_subnet_group
  create_database_subnet_route_table = var.create_database_route_table
  database_subnet_group_name         = "${local.account_prefix}-database-subnet-group"

  azs              = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  public_subnets   = [var.vpc["public_subnet_a"], var.vpc["public_subnet_b"], var.vpc["public_subnet_c"]]
  private_subnets  = [var.vpc["private_subnet_a"], var.vpc["private_subnet_b"], var.vpc["private_subnet_c"]]
  database_subnets = [var.vpc["database_subnet_a"], var.vpc["database_subnet_b"], var.vpc["database_subnet_c"]]
}
