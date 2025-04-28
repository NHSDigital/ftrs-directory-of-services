resource "aws_security_group" "extract_lambda_security_group" {
  name        = "${local.resource_prefix}-${var.extract_name}${local.workspace_suffix}-sg"
  description = "Security group for etl ods extract lambda"

  vpc_id = data.aws_vpc.vpc.id
}
