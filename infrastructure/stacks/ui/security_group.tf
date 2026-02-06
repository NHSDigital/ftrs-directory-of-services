resource "aws_security_group" "ui_lambda_security_group" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-lambda-sg"
  description = "Security group for UI Lambda"
  vpc_id      = data.aws_vpc.vpc[0].id

  tags = {
    Name = "${local.resource_prefix}-lambda-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ui_lambda_allow_cloudfront" {
  count             = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  description       = "Allow CloudFront (or public HTTPS) to access Lambda"
  security_group_id = aws_security_group.ui_lambda_security_group[0].id
  from_port         = var.https_port
  to_port           = var.https_port
  ip_protocol       = "tcp"
  prefix_list_id    = data.aws_ec2_managed_prefix_list.cloudfront_prefix_list.id
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_vpc_security_group_egress_rule" "ui_lambda_allow_egress_to_internet" {
  count             = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  description       = "Allow egress to internet"
  security_group_id = aws_security_group.ui_lambda_security_group[0].id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}
