resource "aws_security_group" "gp_search_lambda_security_group" {
  name        = "${local.resource_prefix}-${var.lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for gp search lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_security_group" "health_check_lambda_security_group" {
  name        = "${local.resource_prefix}-${var.health_check_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for health check lambda for gp search"

  vpc_id = data.aws_vpc.vpc.id
}
