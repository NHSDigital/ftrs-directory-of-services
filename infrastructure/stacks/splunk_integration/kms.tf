# TODO move to account wide existing kms and update local
# module "firehose_encryption_key" {
#   source           = "../../modules/kms"
#   alias_name       = local.kms_aliases.firehose
#   account_id       = data.aws_caller_identity.current.account_id
#   aws_service_name = "firehose.amazonaws.com"
#   description      = "Encryption key for Firehose in ${var.environment} environment"
# }
