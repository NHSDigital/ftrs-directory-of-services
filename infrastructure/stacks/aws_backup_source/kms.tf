module "backup_sns_kms_key" {
  count            = local.stack_enabled == 1 ? 1 : 0
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.backup_sns
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "sns.amazonaws.com"
  description      = "Encryption key for SNS in ${var.environment} environment"
}
