module "sqs_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.sqs
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "sqs.amazonaws.com"
  description      = "Encryption key for SQS queues in ${var.environment} environment"
}

module "secrets_manager_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.secrets_manager
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "secretsmanager.amazonaws.com"
  description      = "Encryption key for Secrets Manager in ${var.environment} environment"
}
