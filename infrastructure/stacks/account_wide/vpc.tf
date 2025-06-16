module "vpc" {
  # Module version: 5.21.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=7c1f791efd61f326ed6102d564d1a65d1eceedf0"

  name                   = "${local.account_prefix}-${var.vpc["name"]}"
  cidr                   = var.vpc["cidr"]
  enable_nat_gateway     = var.enable_nat_gateway
  single_nat_gateway     = var.single_nat_gateway
  one_nat_gateway_per_az = var.one_nat_gateway_per_az

  create_database_subnet_group           = var.create_database_subnet_group
  create_database_subnet_route_table     = var.create_database_route_table
  create_database_internet_gateway_route = var.create_database_internet_gateway_route
  database_subnet_group_name             = "${local.account_prefix}-database-subnet-group"

  azs              = slice(data.aws_availability_zones.available_azs.names, 0, 3)
  public_subnets   = local.public_subnets
  private_subnets  = local.private_subnets
  database_subnets = local.database_subnets

  # NACL configuration
  database_dedicated_network_acl = var.database_dedicated_network_acl
  database_inbound_acl_rules     = local.network_acls["database_inbound"]
  database_outbound_acl_rules    = local.network_acls["database_outbound"]

  private_dedicated_network_acl = var.private_dedicated_network_acl
  private_inbound_acl_rules     = local.network_acls["private_inbound"]
  private_outbound_acl_rules    = local.network_acls["private_outbound"]

  public_dedicated_network_acl = var.public_dedicated_network_acl
  public_inbound_acl_rules     = concat(local.network_acls["default_inbound"], local.network_acls["public_inbound"])
  public_outbound_acl_rules    = concat(local.network_acls["default_outbound"], local.network_acls["public_outbound"])
}

locals {

  public_subnets   = [var.vpc["public_subnet_a"], var.vpc["public_subnet_b"], var.vpc["public_subnet_c"]]
  private_subnets  = [var.vpc["private_subnet_a"], var.vpc["private_subnet_b"], var.vpc["private_subnet_c"]]
  database_subnets = [var.vpc["database_subnet_a"], var.vpc["database_subnet_b"], var.vpc["database_subnet_c"]]

  network_acls = {

    default_inbound = [
      {
        rule_number = 900
        rule_action = "allow"
        from_port   = 1024
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
    ]

    default_outbound = [
      {
        rule_number = 900
        rule_action = "allow"
        from_port   = 1024
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
    ]

    public_inbound = [
      {
        rule_number = 100
        rule_action = "allow"
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
    ]

    public_outbound = [
      {
        rule_number = 100
        rule_action = "allow"
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
    ]

    private_inbound = [
      for i, cidr_block in local.public_subnets : {
        rule_number = 200 + i
        rule_action = "allow"
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = cidr_block
      }
    ]

    private_outbound = [
      for i, cidr_block in local.public_subnets : {
        rule_number = 200 + i
        rule_action = "allow"
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = cidr_block
      }
    ]

    database_inbound = [
      for i, cidr_block in local.public_subnets : {
        rule_number = 300 + i
        rule_action = "allow"
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = cidr_block
      }
    ]

    database_outbound = [
      for i, cidr_block in local.public_subnets : {
        rule_number = 300 + i
        rule_action = "allow"
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = cidr_block
      }
    ]
  }
}
