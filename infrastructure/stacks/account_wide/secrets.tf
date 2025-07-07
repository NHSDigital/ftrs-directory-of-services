resource "aws_secretsmanager_secret" "api_ca_cert_secret" {
  count = contains(["dev", "test"], var.environment) ? 1 : 0
  name  = "/${var.repo_name}/${var.environment}/api-ca-cert"
}

resource "aws_secretsmanager_secret" "api_ca_pk_secret" {
  count = contains(["dev", "test"], var.environment) ? 1 : 0
  name  = "/${var.repo_name}/${var.environment}/api-ca-pk"
}
