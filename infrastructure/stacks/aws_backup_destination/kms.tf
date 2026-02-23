module "backup_destination_kms_key" {
  source = "../../modules/kms"

  alias_name       = local.kms_aliases.backup
  account_id       = var.mgmt_account_id
  aws_service_name = "backup.amazonaws.com"
  description      = "Encryption key for AWS Backup destination vault in ${var.environment} environment"

  additional_policy_statements = [
    {
      Sid    = "AllowSourceAccountCopyIntoVault"
      Effect = "Allow"
      Principal = {
        AWS = local.source_account_root_arns
      }
      Action = [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:CreateGrant",
        "kms:DescribeKey"
      ]
      Resource = "*"
      Condition = {
        StringEquals = {
          "kms:ViaService" = "backup.${var.aws_region}.amazonaws.com"
        }
      }
    }
  ]
}
