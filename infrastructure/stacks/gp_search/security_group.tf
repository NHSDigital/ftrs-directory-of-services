resource "aws_security_group" "gp_search_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for gp search lambda"

  vpc_id = data.aws_vpc.vpc.id
}

# trivy:ignore:aws-vpc-no-public-egress-sgr
resource "aws_vpc_security_group_egress_rule" "lambda_allow_443_egress_to_anywhere" {
  security_group_id = aws_security_group.gp_search_lambda_security_group.id
  from_port         = "443"
  to_port           = "443"
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
  description       = "A rule to allow outgoing connections AWS APIs from the gp search lambda security group"
}
