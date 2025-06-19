resource "aws_ec2_client_vpn_endpoint" "vpn" {
  count = var.environment == "dev" ? 1 : 0

  description            = "${local.account_prefix}-vpn"
  vpc_id                 = module.vpc.vpc_id
  client_cidr_block      = var.vpc["vpn_subnet"]
  server_certificate_arn = data.aws_acm_certificate.vpn_cert[0].arn

  security_group_ids = [aws_security_group.vpn_security_group[0].id]

  transport_protocol = "tcp"
  split_tunnel       = true

  authentication_options {
    type                       = "certificate-authentication"
    root_certificate_chain_arn = data.aws_acm_certificate.vpn_cert[0].arn
  }

  connection_log_options {
    enabled               = true
    cloudwatch_log_group  = aws_cloudwatch_log_group.vpn_log_group[0].name
    cloudwatch_log_stream = aws_cloudwatch_log_stream.vpn_log_stream[0].name
  }
}

resource "aws_ec2_client_vpn_network_association" "database_association" {
  count = var.environment == "dev" ? length(module.vpc.database_subnets) : 0

  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.vpn[0].id
  subnet_id              = module.vpc.database_subnets[count.index]
}

resource "aws_ec2_client_vpn_authorization_rule" "vpn_authorization_rule" {
  for_each = var.environment == "dev" ? { for s in module.vpc.database_subnet_objects : s.id => s } : {}

  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.vpn[0].id
  target_network_cidr    = each.value.cidr_block
  authorize_all_groups   = true
}

resource "aws_security_group" "vpn_security_group" {
  count       = var.environment == "dev" ? 1 : 0
  name        = "${local.account_prefix}-vpn-sg"
  description = "Security Group for Client VPN Endpoint"
  vpc_id      = module.vpc.vpc_id

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_cloudwatch_log_group" "vpn_log_group" {
  count             = var.environment == "dev" ? 1 : 0
  name              = "${local.account_prefix}-vpn-log-group"
  retention_in_days = var.log_group_retention_in_days
}

resource "aws_cloudwatch_log_stream" "vpn_log_stream" {
  count          = var.environment == "dev" ? 1 : 0
  name           = "${local.account_prefix}-vpn-log-stream"
  log_group_name = aws_cloudwatch_log_group.vpn_log_group[0].name
}

resource "aws_secretsmanager_secret" "vpn_ca_cert_secret" {
  count = var.environment == "dev" ? 1 : 0
  name  = "/${var.repo_name}/${var.environment}/vpn-ca-cert"
}

resource "aws_secretsmanager_secret" "vpn_ca_pk_secret" {
  count = var.environment == "dev" ? 1 : 0
  name  = "/${var.repo_name}/${var.environment}/vpn-ca-pk"
}
