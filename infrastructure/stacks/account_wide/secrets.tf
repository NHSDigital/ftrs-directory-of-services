resource "aws_secretsmanager_secret" "api_ca_cert_secret" {
  # checkov:skip=CKV2_AWS_57: Justification: This will be rotated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.repo_name}/${var.environment}/api-ca-cert"
  description = "Public certificate for mTLS authentication"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}

resource "aws_secretsmanager_secret" "api_ca_pk_secret" {
  # checkov:skip=CKV2_AWS_57: Justification: This will be rotated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.repo_name}/${var.environment}/api-ca-pk"
  description = "Private key for mTLS authentication"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}

resource "aws_secretsmanager_secret" "cis2_private_key" {
  # checkov:skip=CKV2_AWS_57: Justification: This will be rotated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/cis2-private-key"
  description = "Private key for CIS2 in ${var.environment} environment"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}

resource "aws_secretsmanager_secret" "cis2_public_key" {
  # checkov:skip=CKV2_AWS_57: Justification: This will be rotated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/cis2-public-key"
  description = "Public key for CIS2 in ${var.environment} environment in JWKS format"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}


resource "aws_secretsmanager_secret" "api_jmeter_pks_key" {
  # checkov:skip=CKV2_AWS_57: Justification: This is generated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.repo_name}/${var.environment}/api-jmeter-pks-key"
  description = "Private key for jmeter mTLS authentication"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}

resource "aws_secretsmanager_secret" "dos_search_proxygen_jwt_credentials" {
  # checkov:skip=CKV2_AWS_57: Justification: This is generated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/dos-search-proxygen-jwt-credentials"
  description = "JWT credentials for DOS Search Proxygen in ${var.environment} environment"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}

resource "aws_secretsmanager_secret" "dos_search_jwt_credentials" {
  # checkov:skip=CKV2_AWS_57: Justification: This is generated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/dos-search/jwt-credentials"
  description = "JWT credentials for NHS Digital Onboarding test application in ${var.environment} environment"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}

resource "aws_secretsmanager_secret" "dos_ingest_proxygen_jwt_credentials" {
  # checkov:skip=CKV2_AWS_57: Justification: This is generated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/dos-ingest-proxygen-jwt-credentials"
  description = "JWT credentials for DOS Ingest Proxygen in ${var.environment} environment"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}

resource "aws_secretsmanager_secret" "dos_ingest_jwt_credentials" {
  # checkov:skip=CKV2_AWS_57: Justification: This is generated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/dos-ingest-jwt-credentials"
  description = "JWT credentials for ODS_ETL application in ${var.environment} environment"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}

resource "aws_secretsmanager_secret" "ods-terminology-credentials" {
  # checkov:skip=CKV2_AWS_57: Justification: This is generated manually.
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/ods-terminology-api-key"
  description = "Credentials for ODS Terminology API in ${var.environment} environment"
  kms_key_id  = module.secrets_manager_encryption_key.key_id
}