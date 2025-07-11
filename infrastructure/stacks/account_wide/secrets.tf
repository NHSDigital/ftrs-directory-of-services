resource "aws_kms_key" "secrets_key" {
  count       = contains(["dev", "test"], var.environment) ? 1 : 0
  description = "KMS CMK for encrypting Secrets Manager secrets"
  # enable_key_rotation = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:sts::${local.account_id}:assumed-role/${data.aws_iam_role.account_github_runner_role_name.name}/*"
        }
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:DescribeKey",
          "kms:GetKeyPolicy",
          "kms:PutKeyPolicy",
          "kms:GenerateDataKey",
          "kms:EnableKeyRotation"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_secretsmanager_secret" "api_ca_cert_secret" {
  count      = contains(["dev", "test"], var.environment) ? 1 : 0
  name       = "/${var.repo_name}/${var.environment}/api-ca-cert"
  kms_key_id = aws_kms_key.secrets_key[0].arn
}

resource "aws_secretsmanager_secret" "api_ca_pk_secret" {
  count      = contains(["dev", "test"], var.environment) ? 1 : 0
  name       = "/${var.repo_name}/${var.environment}/api-ca-pk"
  kms_key_id = aws_kms_key.secrets_key[0].arn
}
