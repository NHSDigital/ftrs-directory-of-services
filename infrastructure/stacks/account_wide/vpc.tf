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
  create_database_nat_gateway_route      = var.create_database_nat_gateway_route
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
  private_inbound_acl_rules     = concat(local.network_acls["private_inbound"], local.network_acls["private_inbound_managed_dynamodb_prefix_list"], local.network_acls["private_inbound_managed_s3_prefix_list"], local.network_acls["private_aws_ip_address_range_inbound"])
  private_outbound_acl_rules    = local.network_acls["private_outbound"]

  public_dedicated_network_acl = var.public_dedicated_network_acl
  public_inbound_acl_rules     = concat(local.network_acls["default_inbound"], local.network_acls["public_inbound"])
  public_outbound_acl_rules    = concat(local.network_acls["default_outbound"], local.network_acls["public_outbound"])

  # VPC Flow Logs
  enable_flow_log           = var.enable_flow_log
  flow_log_destination_type = var.flow_log_destination_type
  flow_log_destination_arn  = module.vpc_flow_logs_s3_bucket.s3_bucket_arn
  flow_log_file_format      = var.flow_log_file_format
}

locals {

  public_subnets   = [var.vpc["public_subnet_a"], var.vpc["public_subnet_b"], var.vpc["public_subnet_c"]]
  private_subnets  = [var.vpc["private_subnet_a"], var.vpc["private_subnet_b"], var.vpc["private_subnet_c"]]
  database_subnets = [var.vpc["database_subnet_a"], var.vpc["database_subnet_b"], var.vpc["database_subnet_c"]]
  vpn_subnets      = var.environment == "dev" ? [var.vpc["vpn_subnet"]] : []

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

    public_inbound = concat([
      {
        rule_number = 100
        rule_action = "allow"
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
      ],
      [
        for i, cidr_block in concat(local.private_subnets, local.database_subnets) : {
          rule_number = 200 + i
          rule_action = "allow"
          from_port   = 0
          to_port     = 65535
          protocol    = "tcp"
          cidr_block  = cidr_block
        }
    ])

    public_outbound = [
      {
        rule_number = 100
        rule_action = "allow"
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
      {
        rule_number     = 101
        rule_action     = "allow"
        from_port       = 443
        to_port         = 443
        protocol        = "tcp"
        ipv6_cidr_block = "::/0"
      }
    ]

    private_inbound = [
      for i, cidr_block in concat(local.public_subnets, local.database_subnets) : {
        rule_number = 200 + i
        rule_action = "allow"
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = cidr_block
      }
    ]

    private_inbound_managed_s3_prefix_list = [for i, cidr in zipmap(
      range(length(data.aws_ec2_managed_prefix_list.s3_prefix_list.entries[*].cidr)),
      data.aws_ec2_managed_prefix_list.s3_prefix_list.entries[*].cidr
      ) :
      {
        rule_number = 300 + i
        rule_action = "allow"
        from_port   = 1024
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = cidr
      }
    ]

    private_inbound_managed_dynamodb_prefix_list = [for i, cidr in zipmap(
      range(length(data.aws_ec2_managed_prefix_list.dynamodb_prefix_list.entries[*].cidr)),
      data.aws_ec2_managed_prefix_list.dynamodb_prefix_list.entries[*].cidr
      ) :
      {
        rule_number = 400 + i
        rule_action = "allow"
        from_port   = 1024
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = cidr
      }
    ]

    private_outbound = [
      {
        rule_number = 200
        rule_action = "allow"
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
      {
        rule_number     = 201
        rule_action     = "allow"
        from_port       = 0
        to_port         = 65535
        protocol        = "tcp"
        ipv6_cidr_block = "::/0"
      }
    ]

    database_inbound = [
      for i, cidr_block in concat(local.private_subnets, local.vpn_subnets) : {
        rule_number = 300 + i
        rule_action = "allow"
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = cidr_block
      }
    ]

    database_outbound = [
      {
        rule_number = 300
        rule_action = "allow"
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
      {
        rule_number     = 301
        rule_action     = "allow"
        from_port       = 0
        to_port         = 65535
        protocol        = "tcp"
        ipv6_cidr_block = "::/0"
      }
    ]
  }

  # Use merged eu-west-2 public CIDRs from the cidr_merge module
  ip_first_octets = distinct([for cidr in data.aws_ip_ranges.eu_west_2_public.cidr_blocks : split(".", cidr)[0]])
  eu_west_2_public_cidrs_merged = [
    for octet in local.ip_first_octets :
    "${octet}.0.0.0/8"
  ]

  private_aws_ip_address_range_inbound = concat([
    for i, cidr_block in local.eu_west_2_public_cidrs_merged : {
      rule_number = 500 + i
      rule_action = "allow"
      from_port   = 0
      to_port     = 65535
      protocol    = "tcp"
      cidr_block  = cidr_block
    }
  ])
}

resource "aws_flow_log" "subnet_flow_log_s3" {
  for_each             = toset(concat(module.vpc.public_subnets, module.vpc.private_subnets, module.vpc.database_subnets))
  log_destination      = module.subnet_flow_logs_s3_bucket.s3_bucket_arn
  log_destination_type = var.flow_log_destination_type
  traffic_type         = "REJECT"
  destination_options {
    per_hour_partition = true
  }
  subnet_id = each.value
}
