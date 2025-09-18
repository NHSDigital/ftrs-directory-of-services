resource "aws_secretsmanager_secret" "proxygen_private_key" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.project}/${var.environment}/proxygen-private-key"
  description = "private key for proxygen"
}

resource "aws_secretsmanager_secret" "proxygen_public_key" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.project}/${var.environment}/proxygen-public-key"
  description = "public key for proxygen"
}

resource "aws_secretsmanager_secret" "proxygen_key_id" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.project}/${var.environment}/proxygen-key-id"
  description = "key id for proxygen"
}

resource "aws_secretsmanager_secret" "proxygen_client_id" {
  # checkov:skip=CKV2_AWS_57: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.project}/${var.environment}/proxygen-client-id"
  description = "client id for proxygen"
}
