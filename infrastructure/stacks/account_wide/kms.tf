resource "aws_kms_key" "secrets_manager_key" {
  count               = contains(["dev", "test"], var.environment) ? 1 : 0
  description         = "KMS CMK for encrypting Secrets Manager secrets"
  enable_key_rotation = true
}

resource "aws_kms_key_policy" "secrets_manager_kms_key_policy" {
  count  = contains(["dev", "test"], var.environment) ? 1 : 0
  key_id = aws_kms_key.secrets_manager_key[0].id
  policy = jsonencode(
    {
      Version = "2012-10-17"
      Id      = "Key-Policy-For-Secrets-Manager"
      Statement = [
        {
          Sid    = "Enable IAM User Permissions"
          Effect = "Allow"
          Principal = {
            AWS = "arn:aws:iam::${local.account_id}:root"
          }
          Action   = "kms:*"
          Resource = "*"
        },
        {
          Sid    = "Enable Secrets Manager Permission"
          Effect = "Allow"
          Principal = {
            Service = "secretsmanager.amazonaws.com"
          }
          Action = [
            "kms:Encrypt*",
            "kms:Decrypt*",
            "kms:ReEncrypt*",
            "kms:GenerateDataKey*",
            "kms:Describe*"
          ]
          Resource = [aws_kms_key.secrets_manager_key[0].arn]
          Condition = {
            StringEquals = {
              "kms:ViaService" = "secretsmanager.${var.aws_region}.amazonaws.com"
            }
          }
        }
      ]
    }
  )
}
