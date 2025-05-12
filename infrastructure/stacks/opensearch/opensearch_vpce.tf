resource "aws_opensearchserverless_vpc_endpoint" "vpc_endpoint" {
  name               = "${var.stack_name}-vpce${local.workspace_suffix}"
  vpc_id             = data.aws_vpc.vpc.id
  subnet_ids         = data.aws_subnets.private_subnets.ids
  security_group_ids = [aws_security_group.opensearch_security_group.id]
}
