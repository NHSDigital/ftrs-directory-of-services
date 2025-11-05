resource "aws_secretsmanager_secret" "session_secret" {
  # checkov:skip=CKV2_AWS_57:TODO - https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  # checkov:skip=CKV_AWS_149:TODO - https://nhsd-jira.digital.nhs.uk/browse/FDOS-405

  name        = "/${var.project}/${var.environment}${local.workspace_suffix}/ui-session-secret"
  description = "Session secret for the DoS UI"

}

resource "random_password" "session_secret" {
  length = 32

  special = true
  upper   = true
  lower   = true
  numeric = true
}

resource "aws_secretsmanager_secret_version" "session_secret" {
  secret_id     = aws_secretsmanager_secret.session_secret.id
  secret_string = random_password.session_secret.result
}
