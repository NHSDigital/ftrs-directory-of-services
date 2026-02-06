resource "aws_iam_role" "firehose_role" {
  name = "${var.project}-${var.environment}-${var.firehose_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "firehose.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# add policy to that firehose role
resource "aws_iam_role_policy" "firehose_policy" {
  role = aws_iam_role.firehose_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat([
      {
        Effect = "Allow"
        Action = [
          "s3:AbortMultipartUpload",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:PutObject"
        ]
        Resource = [
          module.firehose_backup_s3.s3_bucket_arn,
          "${module.firehose_backup_s3.s3_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.firehose_error_log_group.arn}"
      }
      ], var.enable_firehose_sse ? [{
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:ReEncryptFrom",
          "kms:ReEncryptTo"
        ]
        Resource = module.firehose_encryption_key.arn
    }] : [])
  })
}

resource "aws_iam_role" "cw_to_firehose_role" {
  name = "${var.project}-${var.environment}-${var.firehose_name}-cw-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "logs.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "cw_to_firehose_policy" {
  role = aws_iam_role.cw_to_firehose_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "firehose:PutRecord",
        "firehose:PutRecordBatch"
      ]
      Resource = aws_kinesis_firehose_delivery_stream.splunk.arn
    }]
  })
}

