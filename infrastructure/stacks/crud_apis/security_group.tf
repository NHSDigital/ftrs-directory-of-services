resource "aws_security_group" "organisation_api_lambda_security_group" {
  name        = "${local.resource_prefix}-${var.organisation_api_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for crud api lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "organisation_api_allow_443" {
  security_group_id = aws_security_group.organisation_api_lambda_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  to_port           = 443
  from_port         = 443
}
