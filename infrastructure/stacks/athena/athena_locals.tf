locals {
  stack_enabled = var.athena_stack_enabled ? 1 : 0
  rds_secret    = local.stack_enabled == 1 && local.is_primary_environment ? jsondecode(data.aws_secretsmanager_secret_version.target_rds_credentials[0].secret_string) : null
}
