resource "aws_secretsmanager_secret" "apim_api_key" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/apim-api-key"
  description = "API Key for APIM proxy"
}


resource "aws_secretsmanager_secret" "ods-terminology-api-key" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/ods-terminology-api-key"
  description = "API Key for ODS Terminology API"
}
