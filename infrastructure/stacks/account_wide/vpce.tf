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
