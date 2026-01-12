module "app_config" {
  source = "../../modules/app-config"

  name        = "${local.project_prefix}${local.workspace_suffix}"
  description = "AppConfig application for managing feature flags."

  config_profile_type                = "AWS.AppConfig.FeatureFlags"
  hosted_config_version_content_type = "application/json"
  hosted_config_version_content      = "${path.module}/feature_flags.json"

  environments = {
    dev = {
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
