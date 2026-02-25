data "aws_kms_key" "sns" {
  count  = local.stack_enabled
  key_id = local.kms_aliases.sqs
}

data "aws_vpc" "vpc" {
  count = local.stack_enabled
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private" {
  count = local.stack_enabled
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc[0].id]
  }

  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc-private-*"]
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = local.stack_enabled == 1 ? toset(data.aws_subnets.private[0].ids) : toset([])
  id       = each.value
}

data "aws_security_group" "vpce_interface_sg" {
  count = local.stack_enabled
  name  = "${local.account_prefix}-vpce-interface-sg"
}

data "aws_s3_object" "slack_notifier_lambda" {
  count  = local.stack_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-slack-notifier-lambda.zip"
}

data "aws_s3_object" "common_packages_layer" {
  count  = local.stack_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
}

data "aws_s3_object" "python_dependency_layer" {
  count  = local.stack_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-slack-notifier-python-dependency-layer.zip"
}

