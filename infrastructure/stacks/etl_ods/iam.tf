resource "aws_iam_role" "ods_etl_scheduler_invoke_role" {
  name        = "${local.resource_prefix}-ods-etl-scheduler-invoke-role${local.workspace_suffix}"
  description = "IAM role to allow the ODS ETL scheduler to invoke the extractor lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
      {
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        },
        Actions = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:CreateGrant",
          "kms:ReEncrypt"
        ]
        resources = [data.aws_kms_key.scheduler_kms_key.arn]
      }
    ]
  })
}

resource "aws_iam_role_policy" "ods_etl_scheduler_invoke_policy" {
  name   = "${local.resource_prefix}-ods-etl-scheduler-invoke-policy${local.workspace_suffix}"
  role   = aws_iam_role.ods_etl_scheduler_invoke_role.id
  policy = data.aws_iam_policy_document.ods_etl_scheduler_invoke_policy.json
}
