resource "aws_security_group" "vpce_rds_security_group" {
  name        = "${local.account_prefix}-current-dos-rds-vpc-endpoint-sg"
  description = "Security group for VPC Endpoint to RDS (DMS)"
  vpc_id      = module.vpc.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "vpce_allow_all_ingress" {
  security_group_id            = aws_security_group.vpce_rds_security_group.id
  referenced_security_group_id = data.aws_security_group.dms_replication_security_group.id
  description                  = "Allow ingress from DMS replication instance"
  ip_protocol                  = "tcp"
  from_port                    = var.rds_port
  to_port                      = var.rds_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "vpce_allow_all_egress" {
  description       = "Allow all outbound traffic to RDS"
  security_group_id = aws_security_group.vpce_rds_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = var.rds_port
  to_port           = var.rds_port
}

# Security group for Performance EC2 instance
resource "aws_security_group" "performance_ec2_sg" {
  name        = "${local.account_prefix}-performance-sg"
  description = "Security group for Performance EC2 instance (SSM-managed)"
  vpc_id      = module.vpc.vpc_id

  # Explicit egress rules; defining these replaces the default allow-all egress
  # HTTPS egress for software installation, AWS APIs, and performance tests
  # Note: 0.0.0.0/0 here still egresses via a NAT Gateway from private subnets; no inbound exposure.
  # trivy:ignore:aws-vpc-no-public-egress-sgr : FDOS-511 Required HTTPS egress to the internet for installs and AWS APIs; SG egress is least-privilege and NACLs restrict UDP
  egress {
    description = "Allow HTTPS egress (tcp/443) to the internet for installs, AWS APIs, and tests"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # DNS egress (UDP 53) to VPC resolver only (base+2 of VPC CIDR)
  egress {
    description = "Allow DNS egress (udp/53) to VPC resolver only"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = [format("%s/32", cidrhost(var.vpc["cidr"], 2))]
  }

  # NTP egress (UDP 123) to public NTP servers when link-local IP cannot be used
  # trivy:ignore:aws-vpc-no-public-egress-sgr : FDOS-511 Required NTP/UDP 123 egress because link-local IPs cannot be referenced in this environment; NACLs restrict inbound UDP ephemeral responses
  egress {
    description = "Allow NTP egress (udp/123) to public NTP servers"
    from_port   = 123
    to_port     = 123
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.resource_prefix}-performance-sg"
  }
}
