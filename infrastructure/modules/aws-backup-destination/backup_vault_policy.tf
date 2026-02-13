resource "aws_backup_vault_policy" "vault_policy" {
  backup_vault_name = aws_backup_vault.vault.name
  policy            = data.aws_iam_policy_document.vault_policy.json
}

data "aws_iam_policy_document" "vault_policy" {
  #checkov:skip=CKV_AWS_356:AWS Backup vault policy requires wildcard resources for cross-account backup operations
  #checkov:skip=CKV_AWS_111:AWS Backup vault policy requires write access for backup copy operations

  statement {
    sid    = "AllowCopyToVault"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.source_account_id}:root"]
    }

    actions = [
      "backup:CopyIntoBackupVault"
    ]
    resources = ["*"]
  }

  dynamic "statement" {
    for_each = var.enable_vault_protection ? [1] : []
    content {
      sid    = "DenyBackupVaultAccess"
      effect = "Deny"

      principals {
        type        = "AWS"
        identifiers = ["*"]
      }
      actions = [
        "backup:DeleteRecoveryPoint",
        "backup:PutBackupVaultAccessPolicy",
        "backup:UpdateRecoveryPointLifecycle",
        "backup:DeleteBackupVault",
        "backup:StartRestoreJob",
        "backup:DeleteBackupVaultLockConfiguration",
      ]
      resources = ["*"]
    }
  }

  dynamic "statement" {
    for_each = var.enable_vault_protection ? [1] : []
    content {
      sid    = "DenyBackupCopyExceptToSourceAccount"
      effect = "Deny"

      principals {
        type        = "AWS"
        identifiers = ["arn:aws:iam::${var.account_id}:root"]
      }
      actions = [
        "backup:CopyFromBackupVault"
      ]
      resources = ["*"]
      condition {
        test     = "StringNotEquals"
        variable = "backup:CopyTargets"
        values = [
          "arn:aws:backup:${var.region}:${var.source_account_id}:backup-vault:${var.region}-${var.source_account_id}-backup-vault"
        ]
      }
    }
  }
}
