resource "aws_secretsmanager_secret" "api_ca_pk_secret" {
  # checkov:skip=CKV2_AWS_57:TODO - https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149:TODO - https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.repo_name}/${var.environment}/test"
  description = "Test Secret"
}



