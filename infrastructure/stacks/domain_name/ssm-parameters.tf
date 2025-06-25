resource "aws_ssm_parameter" "ssm_aws_account_id" {
  for_each = var.environment == "mgmt" ? { for account in var.aws_accounts : account => account } : {}

  name        = "/${var.project}/${each.key}/aws_account_id"
  description = "ID of the ${each.key} AWS account"
  type        = "SecureString"
  tier        = "Standard"
  value       = "default" # Placeholder, to be manually updated in AWS Console or via CLI later

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}

# locals {
#   allowed_account_ids = [
#     data.aws_ssm_parameter.dev_account_id.value,
#     data.aws_ssm_parameter.test_account_id.value,
#     data.aws_ssm_parameter.prod_account_id.value,
#   ]
# }
