resource "aws_security_group" "rds_security_group" {
  count = local.deploy_databases ? 1 : 0

  name        = "${local.prefix}-rds-sg"
  description = "RDS Security Group"

  vpc_id = data.aws_vpc.vpc.id
}
