resource "aws_security_group" "vpce_rds_security_group" {
  name        = "${local.account_prefix}-vpce-sg"
  description = "Security group for VPC Endpoint to RDS (DMS)"
  vpc_id      = module.vpc.vpc_id
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "vpce_allow_all_egress" {
  description       = "Allow ALL egress to any IP"
  security_group_id = aws_security_group.vpce_rds_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 0
  to_port           = 0
}
