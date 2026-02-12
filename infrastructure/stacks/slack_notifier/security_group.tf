# Security group for Slack notifier Lambda
resource "aws_security_group" "slack_notifier_lambda_sg" {
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
