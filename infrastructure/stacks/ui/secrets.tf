resource "aws_secretsmanager_secret" "session_secret" {
  count = local.stack_enabled
  # checkov:skip=CKV2_AWS_57:TODO - https://nhsd-jira.digital.nhs.uk/browse/FDOS-405
  name        = "/${var.project}/${var.environment}${local.workspace_suffix}/ui-session-secret"
  description = "Session secret for the DoS UI"
  kms_key_id  = data.aws_kms_key.secrets_manager_kms_key.arn
}

resource "random_password" "session_secret" {
  count   = local.stack_enabled
  length  = 32
  special = true
  upper   = true
  lower   = true
  numeric = true
}

resource "aws_secretsmanager_secret_version" "session_secret" {
  count         = local.stack_enabled
  secret_id     = aws_secretsmanager_secret.session_secret[0].id
  secret_string = random_password.session_secret[0].result
}
