resource "aws_security_group" "rds_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count = local.deploy_databases && local.rds_environments ? 1 : 0

  name        = "${local.resource_prefix}-rds-sg"
  description = "RDS Security Group"

  vpc_id = data.aws_vpc.vpc.id
}

data "aws_security_group" "rds_security_group" {
  count = local.deploy_databases && local.rds_environments ? 1 : 0
  name  = "${local.resource_prefix}-rds-sg"
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_vpn" {
  count                        = (local.deploy_databases && local.rds_environments) ? 1 : 0
  description                  = "Allow RDS ingress from VPN"
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = data.aws_security_group.vpn_security_group[0].id
  from_port                    = var.rds_port
  ip_protocol                  = data.aws_ec2_client_vpn_endpoint.client_vpn_endpoint[0].transport_protocol
  to_port                      = var.rds_port
}



resource "aws_security_group" "processor_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.processor_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for processor lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_security_group" "queue_populator_lambda_security_group" {
  count = var.environment == "dev" ? 1 : 0

  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.queue_populator_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for queue populator lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_processor_lambda" {
  count                        = (local.deploy_databases && local.rds_environments) ? 1 : 0
  description                  = "Allow RDS ingress from processor lambda"
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = aws_security_group.processor_lambda_security_group.id
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_queue_populator_lambda" {
  count = var.environment == "dev" ? 1 : 0

  description                  = "Allow RDS ingress from queue populator lambda"
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = aws_security_group.queue_populator_lambda_security_group[0].id
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_egress_rule" "processor_allow_egress_to_internet" {
  description       = "Allow egress to internet"
  security_group_id = aws_security_group.processor_lambda_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_vpc_security_group_egress_rule" "queue_populator_allow_egress_to_internet" {
  count = var.environment == "dev" ? 1 : 0

  description       = "Allow egress to internet"
  security_group_id = aws_security_group.queue_populator_lambda_security_group[0].id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}
