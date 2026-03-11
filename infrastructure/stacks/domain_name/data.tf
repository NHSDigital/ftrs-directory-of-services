data "aws_ssm_parameter" "account_id" {
  for_each = var.environment == "mgmt" ? { for account in var.aws_accounts : account => account } : {}

  name = "/${var.project}/${each.key}/aws_account_id"
}

data "aws_kms_key" "sns_kms_key" {
  count  = var.environment == "mgmt" ? 0 : 1
  key_id = local.kms_aliases.sns
}
