data "aws_kms_key" "sns_kms_key" {
  count  = var.environment == "mgmt" ? 0 : 1
  key_id = local.kms_aliases.sns
}
