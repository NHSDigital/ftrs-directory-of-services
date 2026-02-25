data "aws_iam_policy_document" "version_history_dynamodb_access_policy" {
  count = local.version_history_enabled

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:Query"
    ]
    resources = [
      module.dynamodb_tables["version-history"].dynamodb_table_arn,
      "${module.dynamodb_tables["version-history"].dynamodb_table_arn}/index/*"
    ]
  }
}

data "aws_iam_policy_document" "dynamodb_stream_access_policy" {
  count = local.version_history_enabled

  statement {
    effect = "Allow"
    actions = [
      "dynamodb:DescribeStream",
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:ListStreams"
    ]
    resources = [
      for table in local.table_streams : "${table.table_arn}/stream/*"
    ]
  }
}

data "aws_iam_policy_document" "version_history_kms_access_policy" {
  count = local.version_history_enabled

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey",
      "kms:DescribeKey"
    ]
    resources = [data.aws_kms_key.dynamodb_kms_key.arn]
  }
}
