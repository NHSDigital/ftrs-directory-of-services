resource "aws_security_group" "slack_notifier_lambda_sg" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count       = local.stack_enabled
  name        = "${local.resource_prefix}-lambda-sg"
  description = "Security group for Slack notifier Lambda function"
  vpc_id      = data.aws_vpc.vpc[0].id

  tags = {
    Name = "${local.resource_prefix}-lambda-sg"
  }
}

resource "aws_vpc_security_group_egress_rule" "to_vpc_endpoints" {
  count                        = local.vpc_endpoints_enabled
  security_group_id            = aws_security_group.slack_notifier_lambda_sg[0].id
  description                  = "Allow outbound to VPC endpoints"
  referenced_security_group_id = aws_security_group.vpce_sg[0].id
  ip_protocol                  = "tcp"
  from_port                    = var.https_port
  to_port                      = var.https_port
}

resource "aws_vpc_security_group_egress_rule" "to_slack" {
  count             = local.stack_enabled
  security_group_id = aws_security_group.slack_notifier_lambda_sg[0].id
  description       = "Allow outbound HTTPS for Slack webhooks"
  cidr_ipv4         = var.slack_egress_cidr
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}

resource "aws_security_group" "vpce_sg" {
  # checkov:skip=CKV2_AWS_5: Security group is attached to VPC endpoint in vpc_endpoints.tf
  count       = local.vpc_endpoints_enabled
  name        = "${local.resource_prefix}-vpce-sg"
  description = "Security group for VPC endpoints"
  vpc_id      = data.aws_vpc.vpc[0].id

  tags = {
    Name = "${local.resource_prefix}-vpce-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "vpce_from_lambda" {
  count                        = local.vpc_endpoints_enabled
  security_group_id            = aws_security_group.vpce_sg[0].id
  description                  = "Allow inbound from Lambda"
  referenced_security_group_id = aws_security_group.slack_notifier_lambda_sg[0].id
  ip_protocol                  = "tcp"
  from_port                    = var.https_port
  to_port                      = var.https_port
}
