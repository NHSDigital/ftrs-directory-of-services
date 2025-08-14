resource "aws_secretsmanager_secret" "api_ca_cert_secret" {
  # checkov:skip=CKV2_AWS_57:TODO - https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149:TODO - https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count = contains(["dev", "test"], var.environment) ? 1 : 0
  name  = "/${var.repo_name}/${var.environment}/api-ca-cert"
}

resource "aws_secretsmanager_secret" "api_ca_pk_secret" {
  # checkov:skip=CKV2_AWS_57:TODO - https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149:TODO - https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  count = contains(["dev", "test"], var.environment) ? 1 : 0
  name  = "/${var.repo_name}/${var.environment}/api-ca-pk"
}
