# Consolidated security group for all ETL ODS lambdas
# Reduces ENI consumption from 3 to 1 per workspace
resource "aws_security_group" "etl_ods_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-etl-ods-lambda${local.workspace_suffix}-sg"
  description = "Security group for all etl ods lambdas (extractor, transformer, consumer)"

  vpc_id = data.aws_vpc.vpc.id
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_vpc_security_group_egress_rule" "etl_ods_allow_443" {
  security_group_id = aws_security_group.etl_ods_lambda_security_group.id
  description       = "ETL ODS egress rule to allow HTTPS to internet"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}
