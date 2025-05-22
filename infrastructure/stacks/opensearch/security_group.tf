resource "aws_security_group" "opensearch_security_group" {
  name        = "${local.resource_prefix}-sg${local.workspace_suffix}"
  description = "Allow access from OSIS to OpenSearch"
  vpc_id      = data.aws_vpc.vpc.id
}

resource "aws_security_group_rule" "opensearch_allow_ingress_from_vpc" {
  security_group_id = aws_security_group.opensearch_security_group.id
  description       = "Ingress or Inbound security group rule for OSIS"
  type              = "ingress"
  cidr_blocks       = [for s in data.aws_subnet.private_subnets_details : s.cidr_block]
  protocol          = "tcp"
  from_port         = 443
  to_port           = 443
}

resource "aws_security_group_rule" "opensearch_allow_egress" {
  security_group_id = aws_security_group.opensearch_security_group.id
  description       = "Egress or Outbound security group rule for OSIS"
  type              = "egress"
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
}
