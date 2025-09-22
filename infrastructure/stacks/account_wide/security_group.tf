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
