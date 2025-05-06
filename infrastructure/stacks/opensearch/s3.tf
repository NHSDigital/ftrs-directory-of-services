module "s3" {
  source      = "../../modules/s3"
  bucket_name = "${local.resource_prefix}-${var.ddb_export_bucket_name}"
  versioning  = var.ddb_export_s3_versioning
}

resource "aws_s3_bucket_policy" "ddb_export_policy" {
  bucket = module.s3.s3_bucket_id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "DynamoDBExportAccess"
        Effect = "Allow"
        Principal = {
          Service = "dynamodb.amazonaws.com"
        }
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "${module.s3.s3_bucket_arn}/*"
      }
    ]
  })
}
