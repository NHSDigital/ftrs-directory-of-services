resource "aws_secretsmanager_secret" "dos_ingest_jwt_credentials" {
  # checkov:skip=CKV2_AWS_57: Justification: This will be generated manually .
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/dos-ingest-jwt-credentials"
  description = "JWT token generation credentials"
  kms_key_id  = data.aws_kms_key.secrets_manager_kms_key.arn
}


resource "aws_secretsmanager_secret" "ods-terminology-api-key" {
  # checkov:skip=CKV2_AWS_57: Justification: This will be generated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/ods-terminology-api-key"
  description = "API Key for ODS Terminology API"
  kms_key_id  = data.aws_kms_key.secrets_manager_kms_key.arn
}
