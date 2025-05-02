resource "aws_security_group" "processor_lambda_security_group" {
  name        = "${local.resource_prefix}-${var.extract_name}${local.workspace_suffix}-sg"
  description = "Security group for etl ods extract lambda"
  vpc_id      = data.aws_vpc.vpc.id
}

resource "aws_security_group_rule" "lambda_https_egress" {
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = data.aws_security_group.processor_lambda_security_group.id
  description       = "Allow outbound HTTPS for API access"
}
