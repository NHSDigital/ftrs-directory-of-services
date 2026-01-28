module "app_config" {
  source = "../../modules/app-config"

  name        = "${local.project_prefix}${local.workspace_suffix}"
  description = "AppConfig application for managing feature flags."

  config_profile_type                = "AWS.AppConfig.FeatureFlags"
  hosted_config_version_content_type = "application/json"
  hosted_config_version_content      = "${path.root}/../../toggles/feature-flags.json"

  environments = {
    environment = {
      name        = local.workspace_suffix != "" ? terraform.workspace : var.environment
      description = "Environment for ${local.workspace_suffix != "" ? terraform.workspace : var.environment} deployments."
    }
  }
}



output "appconfig_read_policy_arn" {
  value = module.app_config.appconfig_read_policy_arn
}

output "application_id" {
  value = module.app_config.application_id
}

output "environment_ids" {
  value = module.app_config.environment_ids
}

output "configuration_profile_id" {
  value = module.app_config.configuration_profile_id
}

output "appconfig_extension_layer_arn" {
  value = module.app_config.appconfig_extension_layer_arn
}

data "aws_kms_key" "ssm_kms_key" {
  key_id = local.kms_aliases.ssm
}

# SSM Parameters for cross-stack access
resource "aws_ssm_parameter" "appconfig_application_id" {
  name   = "/${var.project}/${var.environment}/appconfig/application_id"
  type   = "SecureString"
  value  = module.app_config.application_id
  key_id = data.aws_kms_key.ssm_kms_key.arn
}

resource "aws_ssm_parameter" "appconfig_environment_id" {
  name   = "/${var.project}/${var.environment}/appconfig/environment_id"
  type   = "SecureString"
  value  = module.app_config.environment_ids["environment"].environment_id
  key_id = data.aws_kms_key.ssm_kms_key.arn
}

resource "aws_ssm_parameter" "appconfig_configuration_profile_id" {
  name   = "/${var.project}/${var.environment}/appconfig/configuration_profile_id"
  type   = "SecureString"
  value  = module.app_config.configuration_profile_id
  key_id = data.aws_kms_key.ssm_kms_key.arn
}

resource "aws_ssm_parameter" "appconfig_extension_layer_arn" {
  name   = "/${var.project}/${var.environment}/appconfig/extension_layer_arn"
  type   = "SecureString"
  value  = module.app_config.appconfig_extension_layer_arn
  key_id = data.aws_kms_key.ssm_kms_key.arn
}

