resource "aws_security_group" "slack_notifier_lambda_sg" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count       = local.is_primary_environment ? 1 : 0
  name        = "${local.resource_prefix}-lambda-sg"
  description = "Security group for Slack notifier Lambda function"
  vpc_id      = data.aws_vpc.vpc.id

  tags = {
    Name = "${local.resource_prefix}-lambda-sg"
  }
}

# trivy:ignore:aws-vpc-no-public-egress-sgr
resource "aws_vpc_security_group_egress_rule" "slack_notifier_lambda_egress" {
  # checkov:skip=CKV_AWS_382: Lambda needs outbound access to Slack webhook and AWS services
  count             = local.is_primary_environment ? 1 : 0
  security_group_id = aws_security_group.slack_notifier_lambda_sg[0].id
  description       = "Allow all outbound traffic for Slack webhook and AWS services"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

data "aws_security_group" "slack_notifier_lambda_sg_existing" {
  count = local.is_primary_environment ? 0 : 1
  name  = "${local.resource_prefix}-lambda-sg"
}
