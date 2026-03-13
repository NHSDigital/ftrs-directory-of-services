data "aws_kms_key" "sns_kms_key" {
  count  = var.environment == "mgmt" ? 0 : 1
  key_id = local.kms_aliases.sns
}

data "aws_s3_bucket" "trust_store_s3_bucket" {
  bucket = local.s3_trust_store_bucket_name
}

data "aws_s3_bucket" "terraform_state_bucket" {
  bucket = "nhse-${var.environment}-${var.repo_name}-terraform-state"
}

data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_vpc_endpoint" "s3_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.s3"
}

data "aws_vpc_endpoint" "dynamodb_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.dynamodb"
}

data "aws_vpc_endpoint" "sqs_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.sqs"
}

data "aws_vpc_endpoint" "ssm_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.ssm"
}

data "aws_vpc_endpoint" "ssmmessages_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.ssmmessages"
}

data "aws_vpc_endpoint" "ec2messages_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.ec2messages"
}

data "aws_vpc_endpoint" "kms_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.kms"
}

data "aws_vpc_endpoint" "secretsmanager_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.secretsmanager"
}

data "aws_vpc_endpoint" "rds_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.rds"
}

data "aws_vpc_endpoint" "appconfig_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.appconfig"
}

data "aws_vpc_endpoint" "appconfigdata_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.appconfigdata"
}

data "aws_vpc_endpoint" "lambda_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.lambda"
}

data "aws_vpc_endpoint" "logs_vpce" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = "com.amazonaws.${var.aws_region}.logs"
}

data "aws_vpc_endpoint" "current_dos_rds_endpoint" {
  vpc_id       = data.aws_vpc.vpc.id
  service_name = data.aws_ssm_parameter.texas_vpc_endpoint_service_name.name
}

data "aws_ssm_parameter" "texas_vpc_endpoint_service_name" {
  name = "/${local.project_prefix}-account-wide/texas-vpc-endpoint-service-name"
}

data "aws_acm_certificate" "custom_domain_api_cert" {
  count  = var.environment == "mgmt" ? 0 : 1
  domain = "*.${local.root_domain_name}"
}

data "aws_acm_certificate" "custom_domain_cert_cloudfront" {
  count    = var.environment == "mgmt" ? 0 : 1
  domain   = "*.${local.root_domain_name}"
  provider = aws.us-east-1
}
