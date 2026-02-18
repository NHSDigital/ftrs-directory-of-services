resource "aws_vpc_endpoint" "logs" {
  count               = local.vpc_endpoints_enabled
  vpc_id              = data.aws_vpc.vpc[0].id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = data.aws_subnets.private[0].ids
  security_group_ids  = [aws_security_group.vpce_sg[0].id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-logs-vpce"
  }
}
