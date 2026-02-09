resource "aws_iam_role_policy" "athena_dynamodb_policy" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

  name = "${local.resource_prefix}-dynamodb-policy"
  role = aws_iam_role.athena_dynamodb_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudWatchLogsForLambda"
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.resource_prefix}-*:*"
      },
      # checkov:skip=CKV_AWS_355: Justification: VPC ENI management - AWS requires '*'
      # checkov:skip=CKV_AWS_290: Justification: VPC ENI management - AWS requires '*'
      {
        Sid    = "AllowVPCNetworkInterfaceManagement"
        Effect = "Allow",
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AssignPrivateIpAddresses",
          "ec2:UnassignPrivateIpAddresses"
        ],
        Resource = "*" # Required by AWS for Lambda VPC execution
      },
      {
        Sid    = "AllowGlueCatalogAccess"
        Effect = "Allow",
        Action = [
          "glue:GetTableVersions",
          "glue:GetPartitions",
          "glue:GetTables",
          "glue:GetTableVersion",
          "glue:GetDatabases",
          "glue:GetTable",
          "glue:GetPartition",
          "glue:GetDatabase",
          "glue:ListSchemas"
        ],
        Resource = [
          "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:catalog",
          "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:database/${local.resource_prefix}-*",
          "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${local.resource_prefix}-*/*"
        ]
      },
      {
        Sid    = "AllowAthenaQueryExecution"
        Effect = "Allow",
        Action = [
          "athena:GetQueryExecution"
        ],
        Resource = "arn:aws:athena:${var.aws_region}:${data.aws_caller_identity.current.account_id}:workgroup/${local.resource_prefix}-workgroup"
      },
      # checkov:skip=CKV_AWS_355: Justification: S3 bucket listing
      # checkov:skip=CKV_AWS_290: Justification: S3 bucket listing
      {
        Sid    = "AllowListS3Buckets"
        Effect = "Allow",
        Action = [
          "s3:ListAllMyBuckets"
        ],
        Resource = "*"
      },
      {
        Sid    = "AllowDynamoDBReadAccess"
        Effect = "Allow",
        Action = [
          "dynamodb:DescribeTable",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:PartiQLSelect"
        ],
        Resource = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${local.account_prefix}-*"
      },
      # checkov:skip=CKV_AWS_355: Justification: S3 DynamoDB list tables
      # checkov:skip=CKV_AWS_290: Justification: S3 DynamoDB list tables
      {
        Sid    = "AllowDynamoDBListTables"
        Effect = "Allow",
        Action = [
          "dynamodb:ListTables"
        ],
        Resource = "*"
      },
      # checkov:skip=CKV_AWS_355: Justification: ECR image pull
      # checkov:skip=CKV_AWS_290: Justification: ECR image pull
      {
        Sid    = "AllowECRImagePull"
        Effect = "Allow",
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ],
        Resource = "*"
      },
      {
        Sid    = "AllowS3AccessForAthenaSpill"
        Effect = "Allow",
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
          module.athena_spill_bucket[0].s3_bucket_arn,
          "${module.athena_spill_bucket[0].s3_bucket_arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role" "athena_dynamodb_role" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0

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
