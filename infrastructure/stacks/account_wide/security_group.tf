resource "aws_security_group" "vpce_rds_security_group" {
  name        = "${local.account_prefix}-current-dos-rds-vpc-endpoint-sg"
  description = "Security group for VPC Endpoint to RDS (DMS)"
  vpc_id      = module.vpc.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "vpce_allow_all_ingress" {
  security_group_id            = aws_security_group.vpce_rds_security_group.id
  referenced_security_group_id = aws_security_group.dms_replication_security_group.id
  description                  = "Allow ingress from DMS replication instance"
  ip_protocol                  = "tcp"
  from_port                    = var.rds_port
  to_port                      = var.rds_port
}

# Security group for Performance EC2 instance
resource "aws_security_group" "performance_ec2_sg" {
  name        = "${local.account_prefix}-performance-sg"
  description = "Security group for Performance EC2 instance (SSM-managed)"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "${local.resource_prefix}-performance-sg"
  }
}

# HTTPS egress for software installation, AWS APIs, and performance tests
# Note: 0.0.0.0/0 here still egresses via a NAT Gateway from private subnets; no inbound exposure.
# trivy:ignore:aws-vpc-no-public-egress-sgr : FDOS-511 Required HTTPS egress to the internet for installs and AWS APIs; SG egress is least-privilege and NACLs restrict UDP
resource "aws_vpc_security_group_egress_rule" "performance_egress_https" {
  security_group_id = aws_security_group.performance_ec2_sg.id
  description       = "Allow HTTPS egress (tcp/443) to the internet for installs, AWS APIs, and tests"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}

# DNS egress (UDP 53) to VPC resolver only (base+2 of VPC CIDR)
resource "aws_vpc_security_group_egress_rule" "performance_egress_dns_udp" {
  security_group_id = aws_security_group.performance_ec2_sg.id
  description       = "Allow DNS egress (udp/53) to VPC resolver only"
  cidr_ipv4         = format("%s/32", cidrhost(var.vpc["cidr"], 2))
  ip_protocol       = "udp"
  from_port         = var.udp_port
  to_port           = var.udp_port
}

# NTP egress (UDP 123) to public NTP servers when link-local IP cannot be used
# trivy:ignore:aws-vpc-no-public-egress-sgr : FDOS-511 Required NTP/UDP 123 egress because link-local IPs cannot be referenced in this environment; NACLs restrict inbound UDP ephemeral responses
resource "aws_vpc_security_group_egress_rule" "performance_egress_ntp_udp" {
  security_group_id = aws_security_group.performance_ec2_sg.id
  description       = "Allow NTP egress (udp/123) to public NTP servers"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "udp"
  from_port         = var.udp_ntp_port
  to_port           = var.udp_ntp_port
}

# HTTP egress for software installation, AWS APIs, and performance tests
# Note: 0.0.0.0/0 here still egresses via a NAT Gateway from private subnets; no inbound exposure.
# trivy:ignore:aws-vpc-no-public-egress-sgr : FDOS-511 Required HTTPS egress to the internet for installs and AWS APIs; SG egress is least-privilege and NACLs restrict UDP
resource "aws_vpc_security_group_egress_rule" "performance_egress_http" {
  security_group_id = aws_security_group.performance_ec2_sg.id
  description       = "Allow HTTP egress (tcp/80) to the internet for installs"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = var.http_port
  to_port           = var.http_port
}

resource "aws_security_group" "dms_replication_security_group" {
  # checkov:skip=CKV2_AWS_5:Works locally in the checkov checks. Also is used in the file above
  name        = "${local.resource_prefix}-etl-replication-sg"
  description = "Security group for DMS ETL replication instance"
  vpc_id      = module.vpc.vpc_id
  depends_on  = [module.vpc]
}

# Athena RDS Connector Security Group
resource "aws_security_group" "athena_rds_connector_sg" {
  # checkov:skip=CKV2_AWS_5: False positive - Security group attached to Lambda via SAR CloudFormation stack
  count       = var.athena_stack_enabled ? 1 : 0
  name        = "${local.account_prefix}-athena-rds-connector-sg"
  description = "Security group for Athena RDS Connector Lambda"
  vpc_id      = module.vpc.vpc_id
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : Justification: This Athena RDS Connector Lambda requires egress access to the internet for S3 and Secrets Manager, as well as access to the RDS instance.
resource "aws_vpc_security_group_egress_rule" "athena_rds_connector_allow_egress_https" {
  count             = var.athena_stack_enabled ? 1 : 0
  security_group_id = aws_security_group.athena_rds_connector_sg[0].id
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Allow HTTPS for S3 and Secrets Manager"
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}

# Security group for interface VPC endpoints
resource "aws_security_group" "vpce_interface_security_group" {
  name        = "${local.account_prefix}-vpce-interface-sg"
  description = "Security group for interface VPC endpoints (SSM, API Gateway, KMS, Secrets Manager, RDS, AppConfig, SQS)"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "${local.resource_prefix}-vpce-interface-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "vpce_interface_ingress_https" {
  security_group_id = aws_security_group.vpce_interface_security_group.id
  description       = "Allow HTTPS ingress from VPC (return traffic allowed automatically via stateful rules)"
  cidr_ipv4         = var.vpc["cidr"]
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}
