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
  name        = "${local.resource_prefix}-performance-sg"
  description = "Security group for Performance EC2 instance (SSM-managed)"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "${local.resource_prefix}-performance-sg"
  }
}

# Replace broad egress with explicit rules matching gp_search posture
# HTTPS egress for downloads and test traffic
resource "aws_vpc_security_group_egress_rule" "performance_egress_https" {
  security_group_id = aws_security_group.performance_ec2_sg.id
  description       = "Allow HTTPS egress"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}

# DNS egress (UDP 53) for name resolution
resource "aws_vpc_security_group_egress_rule" "performance_egress_dns_udp" {
  security_group_id = aws_security_group.performance_ec2_sg.id
  description       = "Allow DNS egress (UDP 53) to VPC resolver only"
  cidr_ipv4         = format("%s/32", cidrhost(var.vpc["cidr"], 2))
  ip_protocol       = "udp"
  from_port         = 53
  to_port           = 53
}
