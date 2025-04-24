resource "aws_security_group" "gp_search_lambda_security_group" {
  name        = "${local.resource_prefix}-${var.lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for gp search lambda"

  vpc_id = data.aws_vpc.vpc.id
}
