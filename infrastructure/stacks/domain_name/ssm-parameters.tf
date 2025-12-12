resource "aws_ssm_parameter" "ssm_aws_account_id" {
  for_each = var.environment == "mgmt" ? { for account in var.aws_accounts : account => account } : {}

  name        = "/${var.project}/${each.key}/aws_account_id"
  description = "ID of the ${each.key} AWS account"
  type        = "SecureString"
  tier        = "Standard"
  value       = "changeme" # Placeholder, to be manually updated in AWS Console or via CLI later
  key_id      = data.aws_kms_key.ssm_kms_key.arn

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}
