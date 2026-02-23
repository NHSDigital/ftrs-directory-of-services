resource "aws_iam_role" "backup_cross_account_role" {
  name = local.backup_cross_account_role

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = concat(
            [var.mgmt_account_id],
            [
              for account in var.aws_accounts : data.aws_ssm_parameter.account_id[account].value
            ]
          )
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "backup_cross_account_policy" {
  # checkov:skip=CKV_AWS_355: Justification: AWS Backup vault policy requires wildcard resources for cross-account backup operations
  name        = "${local.backup_cross_account_role}-policy"
  description = "Allow cross-account AWS Backup operations in the management account"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSBackupVaultReadOnly"
        Effect = "Allow"
        Action = [
          "backup:ListBackupVaults",
          "backup:DescribeBackupVault"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "backup_cross_account_policy_attachment" {
  role       = aws_iam_role.backup_cross_account_role.name
  policy_arn = aws_iam_policy.backup_cross_account_policy.arn
}
