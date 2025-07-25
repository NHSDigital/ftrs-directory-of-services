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
  count                        = (local.deploy_databases && var.environment == "dev") ? 1 : 0
  description                  = "Allow RDS ingress from VPN"
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = data.aws_security_group.vpn_security_group[0].id
  from_port                    = var.rds_port
  ip_protocol                  = data.aws_ec2_client_vpn_endpoint.client_vpn_endpoint[0].transport_protocol
  to_port                      = var.rds_port
}

resource "aws_security_group" "extract_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.extract_name}${local.workspace_suffix}-sg"
  description = "Security group for extract lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_security_group" "transform_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.transform_name}${local.workspace_suffix}-sg"
  description = "Security group for transform lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_security_group" "load_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.load_name}${local.workspace_suffix}-sg"
  description = "Security group for load lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "lambdas_allow_egress_to_internet" {
  for_each = {
    extract_lambda   = aws_security_group.extract_lambda_security_group.id,
    transform_lambda = aws_security_group.transform_lambda_security_group.id,
    load_lambda      = aws_security_group.load_lambda_security_group.id
  }
  description       = "Allow egress to internet"
  security_group_id = each.value
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_dms" {
  count                        = local.deploy_databases ? 1 : 0
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = aws_security_group.dms_replication_security_group[0].id
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_egress_rule" "rds_allow_egress_to_internet" {
  count             = local.deploy_databases ? 1 : 0
  security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_security_group" "dms_replication_security_group" {
  count       = local.deploy_databases ? 1 : 0
  name        = "${local.resource_prefix}-etl-replication-sg"
  description = "Security group for DMS ETL replication instance"
  vpc_id      = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "dms_replication_allow_ingress_from_rds" {
  count                        = local.deploy_databases ? 1 : 0
  security_group_id            = aws_security_group.dms_replication_security_group[0].id
  referenced_security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_egress_rule" "dms_replication_allow_egress_to_rds" {
  count                        = local.deploy_databases ? 1 : 0
  security_group_id            = aws_security_group.dms_replication_security_group[0].id
  referenced_security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_egress_rule" "dms_replication_allow_egress_to_internet" {
  count             = local.deploy_databases ? 1 : 0
  security_group_id = aws_security_group.dms_replication_security_group[0].id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = "-1"
  ip_protocol       = "-1"
  to_port           = "-1"
}


resource "aws_security_group" "rds_event_listener_lambda_security_group" {
  name        = "${local.resource_prefix}-${var.rds_event_listener_name}${local.workspace_suffix}-sg"
  description = "Security group for RDS event listener lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_to_lambda" {
  count                        = local.deploy_databases ? 1 : 0
  security_group_id            = aws_security_group.rds_event_listener_lambda_security_group.id
  referenced_security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  from_port                    = 443
  ip_protocol                  = "tcp"
  to_port                      = 443
}

resource "aws_vpc_security_group_egress_rule" "rds_event_listener_allow_egress_to_internet" {
  count             = local.deploy_databases ? 1 : 0
  security_group_id = aws_security_group.rds_event_listener_lambda_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = "-1"
  ip_protocol       = "-1"
  to_port           = "-1"
}
