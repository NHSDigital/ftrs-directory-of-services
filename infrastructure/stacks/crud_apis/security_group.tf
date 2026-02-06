# Consolidated security group for all CRUD API lambdas
# Reduces ENI consumption from 3 to 1 per workspace
resource "aws_security_group" "crud_apis_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count = local.is_primary_environment ? 1 : 0

  name        = "${local.resource_prefix}-lambda-sg"
  description = "Security group for all crud api lambdas (organisation, healthcare service, location)"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "crud_apis_allow_dynamodb_access" {
  count = local.is_primary_environment ? 1 : 0

  security_group_id = aws_security_group.crud_apis_lambda_security_group[0].id
  description       = "CRUD APIs egress rule to allow DynamoDB traffic"
  prefix_list_id    = data.aws_prefix_list.dynamodb.id
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}

resource "aws_vpc_security_group_egress_rule" "crud_apis_allow_s3_access" {
  count = local.is_primary_environment ? 1 : 0

  security_group_id = aws_security_group.crud_apis_lambda_security_group[0].id
  description       = "CRUD APIs egress rule to allow S3 traffic"
  prefix_list_id    = data.aws_prefix_list.s3.id
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}
