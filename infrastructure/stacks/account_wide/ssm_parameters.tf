resource "aws_ssm_parameter" "dos_aws_account_id_mgmt" {
  name        = "/dos/${var.environment}/aws_account_id_mgmt"
  description = "Id of the management account"
  type        = "SecureString"
  tier        = "Standard"
  value       = "default"
  key_id      = module.ssm_encryption_key.arn

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}

resource "aws_ssm_parameter" "texas_vpc_endpoint_service_name" {
  name        = "/${local.resource_prefix}/texas-vpc-endpoint-service-name"
  description = "The VPC Endpoint Service Name for the Texas RDS instance"
  type        = "SecureString"
  tier        = "Standard"
  value       = "changeme" # Placeholder, to be manually updated in AWS Console or via CLI later
  key_id      = module.ssm_encryption_key.arn

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}

resource "aws_ssm_parameter" "cis2_client_config" {
  name        = "/${var.project}/${var.environment}/cis2-client-config"
  description = "The CIS2 Client Configuration"
  type        = "SecureString"
  tier        = "Standard"
  value       = "CHANGE_ME" # Placeholder, to be manually updated in AWS Console or via CLI later
  key_id      = module.ssm_encryption_key.arn

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}

resource "aws_ssm_parameter" "cis2_connection_manager" {
  name        = "/${var.project}/${var.environment}/cis2-connection-manager"
  description = "The CIS2 Connection Manager Configuration"
  type        = "SecureString"
  tier        = "Standard"
  value       = "CHANGE_ME" # Placeholder, to be manually updated in AWS Console or via CLI later
  key_id      = module.ssm_encryption_key.arn

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}
