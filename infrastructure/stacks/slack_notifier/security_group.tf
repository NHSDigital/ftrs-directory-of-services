resource "aws_security_group" "slack_notifier_lambda_sg" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-lambda-sg${local.workspace_suffix}"
  description = "Security group for Slack notifier Lambda function"
  vpc_id      = data.aws_vpc.vpc.id

  tags = {
    Name = "${local.resource_prefix}-lambda-sg${local.workspace_suffix}"
  }
}

# trivy:ignore:aws-vpc-no-public-egress-sgr
resource "aws_vpc_security_group_egress_rule" "slack_notifier_lambda_egress" {
  # checkov:skip=CKV_AWS_382: Lambda needs outbound access to Slack webhook and AWS services
  security_group_id = aws_security_group.slack_notifier_lambda_sg.id
  description       = "Allow all outbound traffic for Slack webhook and AWS services"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
