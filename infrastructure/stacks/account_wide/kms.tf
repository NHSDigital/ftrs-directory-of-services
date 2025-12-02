module "sqs_encryption_key" {
  count            = local.is_primary_environment ? 1 : 0
  source           = "../../modules/kms"
  alias_name       = local.sqs_kms_key_alias
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "sqs.amazonaws.com"
  description      = "Encryption key for SQS queues in ${var.environment} environment"
}
