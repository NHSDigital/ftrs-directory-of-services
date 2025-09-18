resource "aws_secretsmanager_secret" "proxygen_private_key" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.project}/${var.environment}/proxygen-private-key"
  description = "Private key for proxygen"
}

resource "aws_secretsmanager_secret" "proxygen_public_key" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.project}/${var.environment}/proxygen-public-key"
  description = "Public key for proxygen"
}

resource "aws_secretsmanager_secret" "proxygen_key_id" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.project}/${var.environment}/proxygen-key-id"
  description = "Key id for proxygen"
}

resource "aws_secretsmanager_secret" "proxygen_client_id" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.project}/${var.environment}/proxygen-client-id"
  description = "Client id for proxygen"
}
