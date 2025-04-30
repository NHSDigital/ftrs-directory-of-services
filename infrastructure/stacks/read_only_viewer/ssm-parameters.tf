resource "aws_ssm_parameter" "dos_aws_account_id_mgmt" {
  name        = "/dos/aws_account_id_mgmt${local.workspace_suffix}"
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
