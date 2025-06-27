data "aws_ssm_parameter" "account_id" {
  for_each = toset(var.aws_accounts)
  name     = "/${var.project}/${each.value}/aws_account_id"
}
