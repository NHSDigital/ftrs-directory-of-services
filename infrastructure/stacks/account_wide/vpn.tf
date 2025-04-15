resource "aws_ec2_client_vpn_endpoint" "vpn" {
  description            = "${local.account_prefix}-vpn"
  vpc_id                 = module.vpc.vpc_id
  client_cidr_block      = var.vpc["vpn_subnet"]
  server_certificate_arn = data.aws_acm_certificate.vpn_cert.arn

  security_group_ids = [aws_security_group.vpn_security_group.id]

  transport_protocol = "tcp"
  split_tunnel       = true

  authentication_options {
    type                       = "certificate-authentication"
    root_certificate_chain_arn = data.aws_acm_certificate.vpn_cert.arn
  }

  connection_log_options {
    enabled               = true
    cloudwatch_log_group  = aws_cloudwatch_log_group.vpn_log_group.name
    cloudwatch_log_stream = aws_cloudwatch_log_stream.vpn_log_stream.name
  }
}

resource "aws_ec2_client_vpn_network_association" "database_association" {
  for_each = toset(module.vpc.database_subnets)

  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.vpn.id
  subnet_id              = each.value
}

resource "aws_ec2_client_vpn_authorization_rule" "vpn_authorization_rule" {
  for_each = { for s in module.vpc.database_subnet_objects : s.id => s }

  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.vpn.id
  target_network_cidr    = each.value.cidr_block
  authorize_all_groups   = true
}

resource "aws_security_group" "vpn_security_group" {
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
  name              = "${local.account_prefix}-vpn-log-group"
  retention_in_days = var.log_group_retention_in_days
}

resource "aws_cloudwatch_log_stream" "vpn_log_stream" {
  name           = "${local.account_prefix}-vpn-log-stream"
  log_group_name = aws_cloudwatch_log_group.vpn_log_group.name
}

resource "aws_secretsmanager_secret" "vpn_ca_cert_secret" {
  name = "/${var.repo_name}/${var.environment}/vpn-ca-cert"
}

resource "aws_secretsmanager_secret" "vpn_ca_pk_secret" {
  name = "/${var.repo_name}/${var.environment}/vpn-ca-pk"
}
