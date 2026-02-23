# trivy:ignore:aws-vpc-no-public-ingress-acl : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-575
# trivy:ignore:aws-autoscaling-enable-at-rest-encryption : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-575
module "vpc" {
  # Module version: 6.0.1
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=a0307d4d1807de60b3868b96ef1b369808289157"

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
  database_inbound_acl_rules     = local.network_acls["default_inbound"]
  database_outbound_acl_rules    = local.network_acls["default_outbound"]

  private_dedicated_network_acl = var.private_dedicated_network_acl
  private_inbound_acl_rules     = local.network_acls["default_inbound"]
  private_outbound_acl_rules    = local.network_acls["default_outbound"]

  public_dedicated_network_acl = var.public_dedicated_network_acl
  public_inbound_acl_rules     = local.network_acls["default_inbound"]
  public_outbound_acl_rules    = local.network_acls["default_outbound"]

  # VPC Flow Logs
  enable_flow_log           = var.enable_flow_log
  flow_log_destination_type = var.flow_log_destination_type
  flow_log_destination_arn  = module.vpc_flow_logs_s3_bucket.s3_bucket_arn
  flow_log_file_format      = var.flow_log_file_format

  # Manage Default NACL rules for the VPC
  default_network_acl_ingress = []
  default_network_acl_egress  = []
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
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
      {
        rule_number     = 901
        rule_action     = "allow"
        from_port       = 0
        to_port         = 65535
        protocol        = "tcp"
        ipv6_cidr_block = "::/0"
      },
      # DNS responses: Allow inbound UDP 32768–65535 only from the VPC resolver (base+2).
      # Matches the outbound UDP 53 rule below. Required because NACLs are stateless and
      # responses target an ephemeral source port on the instance.
      {
        rule_number = 902
        rule_action = "allow"
        from_port   = 32768
        to_port     = 65535
        protocol    = "udp"
        cidr_block  = format("%s/32", cidrhost(var.vpc["cidr"], 2))
      },
      # NTP responses: Allow inbound UDP 32768–65535 from the internet to support public NTP servers.
      # Note: Broader than using the Amazon Time Sync IP; preferred only if a literal IP cannot be used.
      # trivy:ignore:aws-vpc-no-public-ingress-acl : NTP inbound ephemeral (UDP 32768–65535) required for time sync responses
      {
        rule_number = 903
        rule_action = "allow"
        from_port   = 32768
        to_port     = 65535
        protocol    = "udp"
        cidr_block  = "0.0.0.0/0"
      }
    ]

    default_outbound = [
      {
        rule_number = 900
        rule_action = "allow"
        from_port   = 0
        to_port     = 65535
        protocol    = "tcp"
        cidr_block  = "0.0.0.0/0"
      },
      {
        rule_number     = 901
        rule_action     = "allow"
        from_port       = 0
        to_port         = 65535
        protocol        = "tcp"
        ipv6_cidr_block = "::/0"
      },
      # DNS: Allow outbound UDP 53 only to the VPC resolver (base+2).
      # Required for name resolution (e.g., SSM endpoints). Matching inbound UDP responses
      # are permitted by the inbound ephemeral rule above (32768–65535 from the resolver).
      {
        rule_number = 902
        rule_action = "allow"
        from_port   = 53
        to_port     = 53
        protocol    = "udp"
        cidr_block  = format("%s/32", cidrhost(var.vpc["cidr"], 2))
      },
      # NTP: Allow outbound UDP 123 to the internet to support public NTP servers (e.g., time.aws.com, pool.ntp.org).
      # Note: Broader than using the Amazon Time Sync IP; preferred only if a literal IP cannot be used.
      # trivy:ignore:aws-vpc-no-public-egress-acl : NTP egress (UDP 123) required to reach public NTP servers when link-local IP is disallowed
      {
        rule_number = 903
        rule_action = "allow"
        from_port   = 123
        to_port     = 123
        protocol    = "udp"
        cidr_block  = "0.0.0.0/0"
      }
    ]
  }
}

resource "aws_flow_log" "public_subnet_flow_log_s3" {
  count                = length(local.public_subnets)
  log_destination      = module.subnet_flow_logs_s3_bucket.s3_bucket_arn
  log_destination_type = var.flow_log_destination_type
  traffic_type         = "REJECT"
  destination_options {
    per_hour_partition = true
  }
  subnet_id = module.vpc.public_subnets[count.index]
}

resource "aws_flow_log" "private_subnet_flow_log_s3" {
  count                = length(local.private_subnets)
  log_destination      = module.subnet_flow_logs_s3_bucket.s3_bucket_arn
  log_destination_type = var.flow_log_destination_type
  traffic_type         = "REJECT"
  destination_options {
    per_hour_partition = true
  }
  subnet_id = module.vpc.private_subnets[count.index]
}

resource "aws_flow_log" "database_subnet_flow_log_s3" {
  count                = length(local.database_subnets)
  log_destination      = module.subnet_flow_logs_s3_bucket.s3_bucket_arn
  log_destination_type = var.flow_log_destination_type
  traffic_type         = "REJECT"
  destination_options {
    per_hour_partition = true
  }
  subnet_id = module.vpc.database_subnets[count.index]
}
