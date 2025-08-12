resource "aws_secretsmanager_secret" "api_ca_cert_secret" {
  # checkov:skip=CKV2_AWS_57: Temp suppression JIRA-445
  # checkov:skip=CKV_AWS_149: Temp suppression JIRA-445
  count = contains(["dev", "test"], var.environment) ? 1 : 0
  name  = "/${var.repo_name}/${var.environment}/api-ca-cert"
}

resource "aws_secretsmanager_secret" "api_ca_pk_secret" {
  # checkov:skip=CKV2_AWS_57: Temp suppression JIRA-445
  # checkov:skip=CKV_AWS_149: Temp suppression JIRA-445
  count = contains(["dev", "test"], var.environment) ? 1 : 0
  name  = "/${var.repo_name}/${var.environment}/api-ca-pk"
}
