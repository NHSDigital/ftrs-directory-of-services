resource "aws_secretsmanager_secret" "api_ca_cert_secret" {
  count      = contains(["dev", "test"], var.environment) ? 1 : 0
  name       = "/${var.repo_name}/${var.environment}/api-ca-cert"
  kms_key_id = aws_kms_key.secrets_manager_key[0].arn
}

resource "aws_secretsmanager_secret" "api_ca_pk_secret" {
  count      = contains(["dev", "test"], var.environment) ? 1 : 0
  name       = "/${var.repo_name}/${var.environment}/api-ca-pk"
  kms_key_id = aws_kms_key.secrets_manager_key[0].arn
}
