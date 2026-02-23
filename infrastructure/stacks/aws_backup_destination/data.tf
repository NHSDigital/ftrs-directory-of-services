data "aws_ssm_parameter" "account_id" {
  for_each = { for account in var.aws_accounts : account => account }

  name = "/${var.project}/${each.key}/aws_account_id"
}
