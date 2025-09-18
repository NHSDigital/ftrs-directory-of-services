resource "aws_vpc_endpoint" "dynamodb_vpce" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = var.gateway_vpc_endpoint_type
  route_table_ids   = module.vpc.private_route_table_ids

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "AllowAccessFromVPC",
        Effect    = "Allow",
        Principal = "*",
        Action    = "dynamodb:*",
        Resource  = "*",
        Condition = {
          StringEquals = {
            "aws:SourceVpc" : module.vpc.vpc_id
          }
        }
      },
      {
        Sid       = "DenyAccessFromOutsideVPC",
        Effect    = "Deny",
        Principal = "*",
        Action    = "*",
        Resource  = "*",
        Condition = {
          StringNotEquals = {
            "aws:SourceVpc" : module.vpc.vpc_id
          }
        }
      }
    ]
  })

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
  subnet_ids         = module.vpc.private_subnets
  security_group_ids = [aws_security_group.vpce_rds_security_group.id]

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "AllowAccessFromDMS",
        Effect    = "Allow",
        Principal = "*",
        Action    = "rds:*",
        Resource  = "*",
        Condition = {
          StringEquals = {
            "aws:PrincipalService" = "dms.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Name = "${local.resource_prefix}-current-dos-rds-vpc-endpoint"
  }
}
