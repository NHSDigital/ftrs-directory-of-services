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
  subnet_ids         = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids = [aws_security_group.vpce_rds_security_group.id]

  tags = {
    Name = "${local.resource_prefix}-current-dos-rds-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "sqs_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.sqs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-sqs-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "ssm_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ssm"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-ssm-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "ssmmessages_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ssmmessages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-ssmmessages-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "ec2messages_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ec2messages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-ec2messages-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "apigateway_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.execute-api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-apigateway-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "kms_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.kms"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-kms-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "secretsmanager_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-secretsmanager-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "rds_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.rds"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-rds-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "appconfig_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.appconfig"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-appconfig-vpc-endpoint"
  }
}

resource "aws_vpc_endpoint" "appconfigdata_vpce" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.appconfigdata"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [module.vpc.private_subnets[0], module.vpc.private_subnets[1], module.vpc.private_subnets[2]]
  security_group_ids  = [aws_security_group.vpce_interface_security_group.id]
  private_dns_enabled = true

  tags = {
    Name = "${local.resource_prefix}-appconfigdata-vpc-endpoint"
  }
}
