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
    values = ["*private*"]
  }
}

data "aws_s3_object" "slack_notifier_lambda" {
  count  = local.stack_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-slack-notifier-lambda.zip"
}

data "aws_s3_object" "python_dependency_layer" {
  count  = local.stack_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-slack-notifier-python-dependency-layer.zip"
}

data "aws_s3_object" "common_packages_layer" {
  count  = local.stack_enabled
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
}
