resource "aws_security_group" "crud_api_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.crud_api_security_group_name}${local.workspace_suffix}-sg"
  description = "Security group for crud api lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "allow_dynamodb_access_from_crud_api" {
  security_group_id = aws_security_group.crud_api_lambda_security_group.id
  description       = "Crud api egress rule to allow DynamoDB traffic"
  prefix_list_id    = data.aws_prefix_list.dynamodb.id
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_vpc_security_group_egress_rule" "crud_api_allow_443" {
  security_group_id = aws_security_group.crud_api_lambda_security_group.id
  description       = "Crud api egress rule to allow 443"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  to_port           = var.https_port
  from_port         = var.https_port
}