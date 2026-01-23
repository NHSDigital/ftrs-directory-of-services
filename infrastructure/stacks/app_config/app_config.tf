module "app_config" {
  source = "../../modules/app-config"

  name        = "${local.project_prefix}${local.workspace_suffix}"
  description = "AppConfig application for managing feature flags."

  config_profile_type                = "AWS.AppConfig.FeatureFlags"
  hosted_config_version_content_type = "application/json"
  hosted_config_version_content      = abspath("${path.root}/../../toggles/feature-flags.json")

  environments = {
    environment = {
      name        = local.workspace_suffix != "" ? terraform.workspace : var.environment
      description = "Environment for ${local.workspace_suffix != "" ? terraform.workspace : var.environment} deployments."
    }
  }
}

# AppConfig for Alarm Thresholds (dos-search alarms)
module "alarm_thresholds_app_config" {
  source = "../../modules/app-config"

  name        = "${local.project_prefix}-alarm-thresholds${local.workspace_suffix}"
  description = "AppConfig application for managing CloudWatch alarm thresholds."

  config_profile_type                = "AWS.Freeform"
  hosted_config_version_content_type = "application/json"
  hosted_config_version_content      = abspath("${path.root}/../../toggles/alarm-thresholds.json")

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

# Outputs for alarm thresholds AppConfig
output "alarm_thresholds_application_id" {
  value       = module.alarm_thresholds_app_config.application_id
  description = "Application ID for alarm thresholds AppConfig"
}

output "alarm_thresholds_environment_ids" {
  value       = module.alarm_thresholds_app_config.environment_ids
  description = "Environment IDs for alarm thresholds AppConfig"
}

output "alarm_thresholds_configuration_profile_id" {
  value       = module.alarm_thresholds_app_config.configuration_profile_id
  description = "Configuration profile ID for alarm thresholds AppConfig"
}

output "alarm_thresholds_appconfig_read_policy_arn" {
  value       = module.alarm_thresholds_app_config.appconfig_read_policy_arn
  description = "IAM policy ARN for reading alarm thresholds from AppConfig"
}
