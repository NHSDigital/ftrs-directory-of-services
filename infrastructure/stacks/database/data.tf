data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
  count = local.version_history_enabled

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }

  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc-private-*"]
  }
}

data "aws_subnet" "private_subnets_details" {
  for_each = local.version_history_enabled == 1 ? toset(data.aws_subnets.private_subnets[0].ids) : toset([])
  id       = each.value
}

data "aws_prefix_list" "dynamodb" {
  count = local.version_history_enabled
  name  = "com.amazonaws.${var.aws_region}.dynamodb"
}

data "aws_s3_object" "data_migration_lambda_package" { # move to data.tf
  count  = local.version_history_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-data-migration-lambda.zip"
}

data "aws_s3_object" "python_dependency_layer" {
  count  = local.version_history_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-data-migration-python-dependency-layer.zip"
}

data "aws_s3_object" "data_layer" {
  count  = local.version_history_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
}
