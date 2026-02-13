resource "aws_security_group" "version_history_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count = local.version_history_enabled

  name        = "${local.resource_prefix}-version-history-lambda-sg${local.workspace_suffix}"
  description = "Security group for version history lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "allow_dynamodb_access_from_version_history_lambda" {
  count = local.version_history_enabled

  security_group_id = aws_security_group.version_history_lambda_security_group[0].id
  description       = "Version history lambda egress rule to allow DynamoDB traffic"
  prefix_list_id    = data.aws_prefix_list.dynamodb[0].id
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}
