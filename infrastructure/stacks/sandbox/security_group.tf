resource "aws_security_group" "sandbox_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.sandbox_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for sandbox lambda"

  vpc_id = data.aws_vpc.vpc.id
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "sandbox_allow_443" {

  security_group_id = aws_security_group.sandbox_lambda_security_group.id
  description       = "Sandbox egress rule to allow 443"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  to_port           = 443
  from_port         = 443
}
