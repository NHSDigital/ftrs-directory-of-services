# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_security_group" "extractor_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.extractor_name}${local.workspace_suffix}-sg"
  description = "Security group for etl ods extractor lambda"
  vpc_id      = data.aws_vpc.vpc.id
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow outbound HTTPS for API access"
  }
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_security_group" "transformer_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.transformer_name}${local.workspace_suffix}-sg"
  description = "Security group for etl ods transformer lambda"
  vpc_id      = data.aws_vpc.vpc.id
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow outbound HTTPS for API access"
  }
}


# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_security_group" "consumer_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.consumer_name}${local.workspace_suffix}-sg"
  description = "Security group for etl ods consumer lambda"

  vpc_id = data.aws_vpc.vpc.id
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow outbound HTTPS for API access"
  }
}

# Consolidated security group for all ETL ODS lambdas
# Reduces ENI consumption from 3 to 1 per workspace
resource "aws_security_group" "etl_ods_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count = local.is_primary_environment ? 1 : 0

  name        = "${local.resource_prefix}-lambda-sg"
  description = "Security group for all etl ods lambdas (extractor, transformer, consumer)"

  vpc_id = data.aws_vpc.vpc.id
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_vpc_security_group_egress_rule" "etl_ods_allow_443" {
  count = local.is_primary_environment ? 1 : 0

  security_group_id = aws_security_group.etl_ods_lambda_security_group[0].id
  description       = "ETL ODS egress rule to allow HTTPS to internet"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}
