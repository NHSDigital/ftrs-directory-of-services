resource "aws_security_group" "organisation_api_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.organisation_api_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for crud api lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "allow_dynamodb_access_from_organisation_api" {
  security_group_id = aws_security_group.organisation_api_lambda_security_group.id
  description       = "Organisation api egress rule to allow DynamoDB traffic"
  prefix_list_id    = data.aws_prefix_list.dynamodb.id
  ip_protocol       = "tcp"
  from_port         = var.https_port
  to_port           = var.https_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_vpc_security_group_egress_rule" "organisation_api_allow_443" {
  security_group_id = aws_security_group.organisation_api_lambda_security_group.id
  description       = "Organisation api egress rule to allow 443"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  to_port           = var.https_port
  from_port         = var.https_port
}

resource "aws_security_group" "healthcare_service_api_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.healthcare_service_api_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for crud api lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "allow_dynamodb_access_from_healthcare_service_api" {
  security_group_id = aws_security_group.healthcare_service_api_lambda_security_group.id
  description       = "Healthcare service api egress rule to allow DynamoDB traffic"
  prefix_list_id    = data.aws_prefix_list.dynamodb.id
  ip_protocol       = "tcp"
  to_port           = var.https_port
  from_port         = var.https_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_vpc_security_group_egress_rule" "healthcare_service_api_allow_443" {

  security_group_id = aws_security_group.healthcare_service_api_lambda_security_group.id
  description       = "Healthcare service api egress rule to allow 443"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  to_port           = var.https_port
  from_port         = var.https_port
}

resource "aws_security_group" "location_api_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  name        = "${local.resource_prefix}-${var.location_api_lambda_name}${local.workspace_suffix}-sg"
  description = "Security group for crud api lambda"

  vpc_id = data.aws_vpc.vpc.id
}

resource "aws_vpc_security_group_egress_rule" "allow_dynamodb_access_from_location_api" {
  security_group_id = aws_security_group.location_api_lambda_security_group.id
  description       = "Location api egress rule to allow DynamoDB traffic"
  prefix_list_id    = data.aws_prefix_list.dynamodb.id
  ip_protocol       = "tcp"
  to_port           = var.https_port
  from_port         = var.https_port
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_vpc_security_group_egress_rule" "location_api_allow_443" {
  security_group_id = aws_security_group.location_api_lambda_security_group.id
  description       = "Location api egress rule to allow 443"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  to_port           = var.https_port
  from_port         = var.https_port
}

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

# trivy:ignore:aws-vpc-no-public-egress-sgr : TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-386
resource "aws_vpc_security_group_egress_rule" "crud_apis_allow_443" {
  count = local.is_primary_environment ? 1 : 0

  security_group_id = aws_security_group.crud_apis_lambda_security_group[0].id
  description       = "CRUD APIs egress rule to allow HTTPS to internet"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  to_port           = var.https_port
  from_port         = var.https_port
}
