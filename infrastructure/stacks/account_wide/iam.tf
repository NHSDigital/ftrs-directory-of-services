
resource "aws_iam_role_policy" "athena_dynamodb_policy" {
  name = "${local.resource_prefix}-athena-dynamodb-policy"
  role = aws_iam_role.athena_dynamodb_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Action = [
          "glue:GetTableVersions",
          "glue:GetPartitions",
          "glue:GetTables",
          "glue:GetTableVersion",
          "glue:GetDatabases",
          "glue:GetTable",
          "glue:GetPartition",
          "glue:GetDatabase",
          "glue:ListSchemas",
          "athena:GetQueryExecution",
          "s3:ListAllMyBuckets"
        ],
        Resource = "*",
        Effect   = "Allow"
      },
      {
        Action = [
          "dynamodb:DescribeTable",
          "dynamodb:ListTables",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:PartiQLSelect"
        ],
        Resource = "*",
        Effect   = "Allow"
      },
      {
        Action = [
          "dynamodb:ListTables",
        ],
        Resource = "*",
        Effect   = "Allow"
      },
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetLifecycleConfiguration",
          "s3:PutLifecycleConfiguration",
          "s3:DeleteObject"
        ],
        Resource = [
          module.athena_spill_bucket.s3_bucket_arn,
          "${module.athena_spill_bucket.s3_bucket_arn}/*"
        ],
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_iam_role" "athena_dynamodb_role" {
  name = "${local.resource_prefix}-athena-dynamodb-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}
