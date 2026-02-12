resource "aws_security_group" "slack_notifier_lambda_sg" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  # checkov:skip=CKV_AWS_382: Lambda needs outbound access to Slack webhook and AWS services
  name        = "${local.resource_prefix}-lambda-sg${local.workspace_suffix}"
  description = "Security group for Slack notifier Lambda function"
  vpc_id      = data.aws_vpc.vpc.id

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.resource_prefix}-lambda-sg${local.workspace_suffix}"
  }
}

data "aws_security_group" "slack_notifier_lambda_sg_existing" {
  count = local.is_primary_environment ? 0 : 1
  name  = "${local.resource_prefix}-lambda-sg"
}
