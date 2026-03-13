resource "aws_security_group" "dos_search_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count = local.is_primary_environment ? 1 : 0

  name        = "${local.resource_prefix}-lambda-sg"
  description = "Security group for dos-search lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "allow_dynamodb_access_from_dos_search_lambda" {
  count = local.is_primary_environment ? 1 : 0

  security_group_id = aws_security_group.dos_search_lambda_security_group[0].id
  description       = "dos-search egress rule to allow DynamoDB traffic"
  prefix_list_id    = data.aws_prefix_list.dynamodb.id
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}

resource "aws_vpc_security_group_egress_rule" "allow_vpc_endpoints_access_from_dos_search_lambda" {
  count = local.is_primary_environment ? 1 : 0

  description                  = "Allow egress to VPC endpoints (Secrets Manager, SQS, KMS, AppConfig)"
  security_group_id            = aws_security_group.dos_search_lambda_security_group[0].id
  referenced_security_group_id = data.aws_security_group.vpce_interface_security_group.id
  ip_protocol                  = "tcp"
  from_port                    = var.https_port
  to_port                      = var.https_port
}
