resource "aws_security_group" "rds_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count = local.is_primary_environment ? 1 : 0

  name        = "${local.resource_prefix}-rds-sg"
  description = "RDS Security Group"

  vpc_id = data.aws_vpc.vpc.id
}

data "aws_security_group" "rds_security_group" {
  count = local.is_primary_environment ? 0 : 1
  name  = "${local.resource_prefix}-rds-sg"
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_vpn" {
  count                        = (local.is_primary_environment && var.environment == "dev") ? 1 : 0
  description                  = "Allow RDS ingress from VPN"
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = data.aws_security_group.vpn_security_group[0].id
  from_port                    = var.rds_port
  ip_protocol                  = data.aws_ec2_client_vpn_endpoint.client_vpn_endpoint[0].transport_protocol
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_ingress_rule" "rds_ingress_from_connector" {
  count                        = local.is_primary_environment ? 0 : 1
  security_group_id            = aws_security_group.rds_security_group[0].id
  referenced_security_group_id = data.aws_security_group.rds_connector_security_group.id
  description                  = "Allow incoming Postgres from Athena RDS Connector Lambda"
  ip_protocol                  = "tcp"
  from_port                    = var.rds_port
  to_port                      = var.rds_port
}

resource "aws_security_group" "processor_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.processor_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for processor lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_processor_lambda" {
  description                  = "Allow RDS ingress from processor lambda"
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = aws_security_group.processor_lambda_security_group.id
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_egress_rule" "processor_allow_egress_to_rds" {
  description                  = "Allow egress to RDS"
  security_group_id            = aws_security_group.processor_lambda_security_group.id
  referenced_security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_egress_rule" "allow_dynamodb_access_from_processor_lambda" {
  security_group_id = aws_security_group.processor_lambda_security_group.id
  description       = "Processor lambda egress rule to allow DynamoDB traffic"
  prefix_list_id    = data.aws_prefix_list.dynamodb.id
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "processor_allow_egress_to_internet" {
  description       = "Allow egress to internet"
  security_group_id = aws_security_group.processor_lambda_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = var.https_port
  ip_protocol       = "tcp"
  to_port           = var.https_port
}

resource "aws_security_group" "queue_populator_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.queue_populator_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for queue populator lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_queue_populator_lambda" {
  description                  = "Allow RDS ingress from queue populator lambda"
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = aws_security_group.queue_populator_lambda_security_group.id
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_egress_rule" "queue_populator_allow_egress_to_rds" {
  description                  = "Allow egress to RDS"
  security_group_id            = aws_security_group.queue_populator_lambda_security_group.id
  referenced_security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "queue_populator_allow_egress_to_internet" {
  description       = "Allow egress to internet"
  security_group_id = aws_security_group.queue_populator_lambda_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = var.https_port
  ip_protocol       = "tcp"
  to_port           = var.https_port
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_dms" {
  count                        = local.is_primary_environment ? 1 : 0
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = aws_security_group.dms_replication_security_group[0].id
  description                  = "Allow ingress on port ${var.rds_port} from DMS replication security group"
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
#resource "aws_vpc_security_group_egress_rule" "rds_allow_egress_to_internet" {
#  count             = local.is_primary_environment ? 1 : 0
#  security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
#  description       = "Allow egress to internet on port ${var.https_port}"
#  cidr_ipv4         = "0.0.0.0/0"
#  from_port         = var.https_port
#  ip_protocol       = "tcp"
#  to_port           = var.https_port
#}


resource "aws_security_group" "dms_replication_security_group" {
  count       = local.is_primary_environment ? 1 : 0
  name        = "${local.resource_prefix}-etl-replication-sg"
  description = "Security group for DMS ETL replication instance"
  vpc_id      = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "dms_replication_allow_ingress_from_rds" {
  count                        = local.is_primary_environment ? 1 : 0
  security_group_id            = aws_security_group.dms_replication_security_group[0].id
  referenced_security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  description                  = "Allow ingress on port ${var.rds_port} from RDS security group"
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_ingress_rule" "dms_replication_allow_ingress_from_vpce" {
  count                        = local.is_primary_environment ? 1 : 0
  security_group_id            = aws_security_group.dms_replication_security_group[0].id
  referenced_security_group_id = data.aws_security_group.vpce_rds_security_group.id
  description                  = "Allow ingress on port ${var.rds_port} from Live DoS VPC Endpoint"
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_vpc_security_group_egress_rule" "dms_replication_allow_egress_to_rds" {
  count                        = local.is_primary_environment ? 1 : 0
  security_group_id            = aws_security_group.dms_replication_security_group[0].id
  referenced_security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  description                  = "Allow egress on port ${var.rds_port} to RDS security group"
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "dms_replication_allow_egress_https" {
  count             = local.is_primary_environment ? 1 : 0
  security_group_id = aws_security_group.dms_replication_security_group[0].id
  description       = "Allow egress to internet on HTTPS port"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = var.https_port
  ip_protocol       = "tcp"
  to_port           = var.https_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "dms_replication_allow_egress_dns" {
  count             = local.is_primary_environment ? 1 : 0
  security_group_id = aws_security_group.dms_replication_security_group[0].id
  description       = "Allow egress for DNS resolution"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = var.dns_port
  ip_protocol       = "tcp"
  to_port           = var.dns_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "dms_replication_allow_egress_dns_udp" {
  count             = local.is_primary_environment ? 1 : 0
  security_group_id = aws_security_group.dms_replication_security_group[0].id
  description       = "Allow egress for DNS resolution (UDP)"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = var.dns_port
  ip_protocol       = "udp"
  to_port           = var.dns_port
}

resource "aws_vpc_security_group_egress_rule" "dms_replication_allow_egress_vpce" {
  count                        = local.is_primary_environment ? 1 : 0
  security_group_id            = aws_security_group.dms_replication_security_group[0].id
  referenced_security_group_id = data.aws_security_group.vpce_rds_security_group.id
  description                  = "Allow egress to Live DoS VPC Endpoint"
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

resource "aws_security_group" "rds_event_listener_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count       = local.is_primary_environment ? 1 : 0
  name        = "${local.resource_prefix}-${var.rds_event_listener_lambda_name}-sg"
  description = "Security group for RDS event listener lambda"

  vpc_id = data.aws_vpc.vpc.id
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_to_lambda" {
  count                        = local.is_primary_environment ? 1 : 0
  security_group_id            = aws_security_group.rds_event_listener_lambda_security_group[0].id
  referenced_security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  description                  = "Allow ingress on port ${var.https_port} from RDS security group"
  from_port                    = var.https_port
  ip_protocol                  = "tcp"
  to_port                      = var.https_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "rds_event_listener_allow_egress_to_internet" {
  count             = local.is_primary_environment ? 1 : 0
  security_group_id = aws_security_group.rds_event_listener_lambda_security_group[0].id
  description       = "Allow egress to internet on port ${var.https_port}"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = var.https_port
  ip_protocol       = "tcp"
  to_port           = var.https_port
}

resource "aws_security_group" "dms_db_setup_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count       = local.is_primary_environment ? 1 : 0
  name        = "${local.resource_prefix}-${var.dms_db_lambda_name}-sg"
  description = "Security group for DMS DB Setup lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "dms_db_setup_allow_ingress_to_lambda" {
  count             = local.is_primary_environment ? 1 : 0
  security_group_id = aws_security_group.dms_db_setup_lambda_security_group[0].id
  description       = "Allow ingress on from anywhere on port ${var.https_port}"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = var.https_port
  ip_protocol       = "tcp"
  to_port           = var.https_port
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_dms_db_setup" {
  count                        = local.is_primary_environment ? 1 : 0
  security_group_id            = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  referenced_security_group_id = aws_security_group.dms_db_setup_lambda_security_group[0].id
  description                  = "Allow ingress on port ${var.rds_port} from DMS DB Setup lambda security group"
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "dms_db_setup_allow_egress_to_rds" {
  count                        = local.is_primary_environment ? 1 : 0
  security_group_id            = aws_security_group.dms_db_setup_lambda_security_group[0].id
  description                  = "Allow egress to database on port ${var.rds_port}"
  referenced_security_group_id = try(aws_security_group.rds_security_group[0].id, data.aws_security_group.rds_security_group[0].id)
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "dms_db_setup_allow_egress_to_internet" {
  count             = local.is_primary_environment ? 1 : 0
  security_group_id = aws_security_group.dms_db_setup_lambda_security_group[0].id
  description       = "Allow egress to database on port ${var.https_port}"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = var.https_port
  ip_protocol       = "tcp"
  to_port           = var.https_port
}
