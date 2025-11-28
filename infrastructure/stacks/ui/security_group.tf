resource "aws_security_group" "ui_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-lambda-sg${local.workspace_suffix}"
  description = "Security group for UI Lambda"
  vpc_id      = data.aws_vpc.vpc.id

  tags = {
    Name = "${local.resource_prefix}-lambda-sg"
  }
}

# trivy:ignore:aws-vpc-no-public-ingress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_ingress_rule" "ui_lambda_allow_cloudfront" {
  description       = "Allow CloudFront (or public HTTPS) to access Lambda"
  security_group_id = aws_security_group.ui_lambda_security_group.id
  from_port         = var.https_port
  to_port           = var.https_port
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-511
resource "aws_vpc_security_group_egress_rule" "ui_lambda_allow_egress_to_internet" {
  description       = "Allow egress to internet"
  security_group_id = aws_security_group.ui_lambda_security_group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}
