resource "aws_ssm_parameter" "dos_aws_account_id_mgmt" {
  name        = "/dos/${var.environment}/aws_account_id_mgmt"
  description = "Id of the management account"
  type        = "SecureString"
  tier        = "Standard"
  value       = "default"

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}
