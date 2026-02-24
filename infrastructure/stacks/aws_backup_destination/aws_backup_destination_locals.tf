locals {
  source_account_ids = [
    for account in var.aws_accounts : data.aws_ssm_parameter.account_id[account].value
  ]
  source_account_root_arns = [
    for account_id in local.source_account_ids : "arn:aws:iam::${account_id}:root"
  ]
}
