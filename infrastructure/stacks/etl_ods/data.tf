data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_prefix}-vpc"]
  }
}

data "aws_subnets" "private_subnets" {
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
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}

data "aws_iam_policy_document" "s3_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "${module.etl_ods_store_bucket.s3_bucket_arn}/",
      "${module.etl_ods_store_bucket.s3_bucket_arn}/*",
    ]
  }
}

data "aws_iam_policy_document" "sqs_access_policy" {
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:SendMessage",
      "sqs:GetQueueUrl"
    ]
    resources = [
      aws_sqs_queue.transformed_queue.arn,
    ]
  }
}
# may need to change to APIM from crud
data "aws_iam_policy_document" "ssm_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${var.project}-${var.environment}-crud-apis${local.workspace_suffix}/endpoint"
    ]
  }
}

# TODO: FDOS-378 - This is overly permissive and should be resolved when we have control over stack deployment order.
data "aws_iam_policy_document" "execute_api_policy" {
  statement {
    effect = "Allow"
    actions = [
      "execute-api:Invoke"
    ]
    resources = [
      "arn:aws:execute-api:*:*:*/*/*/*/*"
    ]
  }

}

data "aws_iam_policy_document" "ssm_api_key_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${var.project}-${var.environment}-crud-apis${local.workspace_suffix}/crud_api-key"
    ]
  }
}
