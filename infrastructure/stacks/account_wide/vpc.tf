module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.18.0"

  name               = "${local.prefix}-${var.vpc["name"]}"
  cidr               = var.vpc["cidr"]
  enable_nat_gateway = var.enable_nat_gateway
  single_nat_gateway = var.single_nat_gateway

  create_database_subnet_group = var.create_database_subnet_group
  database_subnet_group_name   = "${local.prefix}-database-subnet-group"

  azs              = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  public_subnets   = [var.vpc["public_subnet_a"], var.vpc["public_subnet_b"], var.vpc["public_subnet_c"]]
  private_subnets  = [var.vpc["private_subnet_a"], var.vpc["private_subnet_b"], var.vpc["private_subnet_c"]]
  database_subnets = [var.vpc["database_subnet_a"], var.vpc["database_subnet_b"], var.vpc["database_subnet_c"]]
}
