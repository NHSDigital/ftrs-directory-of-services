resource "aws_kms_key" "aws_backup_key" {
  description             = "AWS Backup KMS Key"
  deletion_window_in_days = var.kms_deletion_window_in_days
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.backup_key_policy.json
}

resource "aws_kms_alias" "backup_key" {
  name          = "alias/${var.resource_prefix}-kms"
  target_key_id = aws_kms_key.aws_backup_key.key_id
}

data "aws_iam_policy_document" "backup_key_policy" {
  #checkov:skip=CKV_AWS_109:See (CERSS-25168) for more info
  #checkov:skip=CKV_AWS_111:See (CERSS-25169) for more info
  #checkov:skip=CKV_AWS_356:KMS key policy requires wildcard resources for AWS Backup service operations
  statement {
    sid = "AllowBackupUseOfKey"
    principals {
      type        = "Service"
      identifiers = ["backup.amazonaws.com"]
    }
    actions   = ["kms:GenerateDataKey", "kms:Decrypt", "kms:Encrypt"]
    resources = ["*"]
  }
  statement {
    sid = "EnableIAMUserPermissions"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root", data.aws_caller_identity.current.arn]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  # Allow destination account to decrypt for cross-account backup copy
  dynamic "statement" {
    for_each = var.backup_copy_vault_account_id != "" ? [1] : []
    content {
      sid = "AllowDestinationAccountDecrypt"
      principals {
        type        = "AWS"
        identifiers = ["arn:aws:iam::${var.backup_copy_vault_account_id}:root"]
      }
      actions = [
        "kms:Decrypt",
        "kms:DescribeKey"
      ]
      resources = ["*"]
      condition {
        test     = "StringEquals"
        variable = "kms:ViaService"
        values   = ["backup.${var.aws_region}.amazonaws.com"]
      }
    }
  }
}
