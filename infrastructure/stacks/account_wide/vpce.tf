resource "aws_vpc_endpoint" "dynamodb_vpce" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = var.gateway_vpc_endpoint_type
  route_table_ids   = module.vpc.private_route_table_ids

  tags = {
    Name = "${local.resource_prefix}-dynamodb-gateway-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "s3_vpce" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = var.gateway_vpc_endpoint_type
  route_table_ids   = module.vpc.private_route_table_ids

  tags = {
    Name = "${local.resource_prefix}-s3-gateway-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "current_dos_rds_endpoint" {
  vpc_id             = module.vpc.vpc_id
  service_name       = aws_ssm_parameter.texas_vpc_endpoint_service_name.value
  vpc_endpoint_type  = "Interface"
  subnet_ids         = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids = [aws_security_group.vpce_rds_security_group.id]

  tags = {
    Name = "${local.resource_prefix}-current-dos-rds-vpc-endpoint"
  }
}

# Create Interface VPC Endpoints using for_each loop
resource "aws_vpc_endpoint" "interface_vpce" {
  for_each = local.interface_vpc_endpoints

  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.${each.value}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-${each.key}-vpc-endpoint"
  }
}

# Lambda VPC Endpoint (required for RDS Lambda invocation)
resource "aws_vpc_endpoint" "lambda_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.lambda"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-lambda-vpc-endpoint"
  }
}

# CloudWatch Logs VPC Endpoint (required for RDS log exports)
resource "aws_vpc_endpoint" "logs_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-logs-vpc-endpoint"
  }
}
