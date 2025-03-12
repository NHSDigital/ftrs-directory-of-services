resource "aws_security_group" "rds_security_group" {
  count = local.deploy_databases ? 1 : 0

  name        = "${local.prefix}-rds-sg"
  description = "RDS Security Group"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_vpn" {
  count                        = local.deploy_databases ? 1 : 0
  security_group_id            = aws_security_group.rds_security_group[0].id
  referenced_security_group_id = data.aws_security_group.vpn_security_group.id
  from_port                    = var.rds_port
  ip_protocol                  = data.aws_ec2_client_vpn_endpoint.client_vpn_endpoint.transport_protocol
  to_port                      = var.rds_port
}
