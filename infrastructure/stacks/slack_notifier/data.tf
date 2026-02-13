data "aws_kms_key" "sns" {
  key_id = local.kms_aliases.sqs
}

data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }

  filter {
    name   = "tag:Name"
    values = ["*private*"]
  }
}

data "aws_s3_object" "slack_notifier_lambda" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-slack-notifier-lambda.zip"
}

data "aws_s3_object" "python_dependency_layer" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-slack-notifier-python-dependency-layer.zip"
}

data "aws_s3_object" "common_packages_layer" {
  bucket = local.artefacts_bucket
  key    = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
}
