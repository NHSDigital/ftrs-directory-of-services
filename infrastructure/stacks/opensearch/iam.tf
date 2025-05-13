resource "aws_iam_role" "osis_pipelines_role" {
  name = "${local.resource_prefix}-osis-role${local.workspace_suffix}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = [
            "osis-pipelines.amazonaws.com"
          ]
        }
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy" "osis_pipelines_policy" {
  name = "${local.resource_prefix}-osis-policy${local.workspace_suffix}"
  role = aws_iam_role.osis_pipelines_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:DescribeTable",
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator",
          "dynamodb:ListStreams",
          "dynamodb:DescribeStream",
          "dynamodb:Scan",
          "dynamodb:DescribeContinuousBackups",
          "dynamodb:ExportTableToPointInTime",
          "dynamodb:DescribeExport"
        ]
        Resource = flatten([
          for tablename in var.dynamodb_table_names_for_opensearch :
          [
            "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/${local.resource_prefix}-${tablename}${local.workspace_suffix}",
            "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/${local.resource_prefix}-${tablename}${local.workspace_suffix}/export/*",
            "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/${local.resource_prefix}-${tablename}${local.workspace_suffix}/stream/*"
          ]
        ])
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:AbortMultipartUpload",
          "s3:PutObjectAcl"
        ]
        Resource = [
          module.s3.s3_bucket_arn,
          "${module.s3.s3_bucket_arn}/*",
          module.s3_opensearch_pipeline_dlq_bucket.s3_bucket_arn,
          "${module.s3_opensearch_pipeline_dlq_bucket.s3_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "osis:Ingest",
          "osis:GetPipeline",
          "osis:CreatePipeline",
          "osis:DescribePipeline",
          "osis:StartPipeline",
          "osis:UpdatePipeline",
          "osis:DeletePipeline",
          "osis:ListPipelines"
        ]
        Resource = [
          "*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "aoss:APIAccessAll",
          "aoss:BatchGetCollection",
          "aoss:CreateSecurityPolicy",
          "aoss:GetSecurityPolicy",
          "aoss:UpdateSecurityPolicy",
          "aoss:DescribeIndex",
          "aoss:ReadDocument",
          "aoss:DescribeCollectionItems",
          "aoss:ReadCollectionItems"
        ]
        Resource = [
          "*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents",
          "logs:CreateLogGroup",
          "logs:CreateLogStream"
        ]
        Resource = aws_cloudwatch_log_group.osis_pipeline_cloudwatch_log_group.arn
      }
    ]
  })
}
