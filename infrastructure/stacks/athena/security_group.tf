resource "aws_security_group" "rds_connector_sg" {
  # checkov:skip=CKV2_AWS_5: False positive - Security group attached to Lambda via SAR CloudFormation stack
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  name        = "${local.resource_prefix}-rds-connector-sg"
  description = "Security group for Athena RDS Connector Lambda"
  vpc_id      = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "rds_connector_allow_egress_to_rds" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  security_group_id            = aws_security_group.rds_connector_sg[0].id
  referenced_security_group_id = data.aws_security_group.dms_replication_security_group.id
  description                  = "Allow Lambda connector to connect to RDS"
  ip_protocol                  = "tcp"
  from_port                    = var.rds_port
  to_port                      = var.rds_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : Justification: This Athena RDS Connector Lambda requires egress access to the internet for S3 and Secrets Manager, as well as access to the RDS instance.
resource "aws_vpc_security_group_egress_rule" "rds_connector_allow_egress_https" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  security_group_id = aws_security_group.rds_connector_sg[0].id
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Allow HTTPS for S3 and Secrets Manager"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_lambda" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  security_group_id            = data.aws_security_group.dms_replication_security_group.id
  referenced_security_group_id = aws_security_group.rds_connector_sg[0].id
  description                  = "Allow Athena Lambda connector to connect to RDS"
  ip_protocol                  = "tcp"
  from_port                    = var.rds_port
  to_port                      = var.rds_port
}
