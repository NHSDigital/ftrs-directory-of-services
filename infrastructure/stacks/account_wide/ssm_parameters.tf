resource "aws_ssm_parameter" "dos_aws_account_id_mgmt" {
  # checkov:skip=CKV_AWS_337: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-402
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

resource "aws_ssm_parameter" "texas_vpc_endpoint_service_name" {
  # checkov:skip=CKV_AWS_337: TODO https://nhsd-jira.digital.nhs.uk/browse/FDOS-402
  name        = "/${local.resource_prefix}/texas-vpc-endpoint-service-name"
  description = "The VPC Endpoint Service Name for the Texas RDS instance"
  type        = "SecureString"
  tier        = "Standard"
  value       = "changeme" # Placeholder, to be manually updated in AWS Console or via CLI later

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}
