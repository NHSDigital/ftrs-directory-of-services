locals {
  appconfigs = {
    alarm_thresholds = {
      name        = "${local.project_prefix}-alarm-thresholds${local.workspace_suffix}"
      description = "AppConfig application for managing CloudWatch alarm thresholds."
      config_file = abspath("${path.root}/../dos_search/toggles/alarm-thresholds.json")
    }
  }
}

module "app_config" {
  for_each = local.appconfigs

  source = "../../modules/app-config"

  name        = each.value.name
  description = each.value.description

  config_profile_type                = "AWS.Freeform"
  hosted_config_version_content_type = "application/json"
  hosted_config_version_content      = each.value.config_file

  environments = {
    environment = {
      name        = local.workspace_suffix != "" ? terraform.workspace : var.environment
      description = "Environment for ${local.workspace_suffix != "" ? terraform.workspace : var.environment} deployments."
    }
  }
}

output "alarm_thresholds_application_id" {
  value       = module.app_config["alarm_thresholds"].application_id
  description = "Application ID for alarm thresholds AppConfig"
}

output "alarm_thresholds_environment_ids" {
  value       = module.app_config["alarm_thresholds"].environment_ids
  description = "Environment IDs for alarm thresholds AppConfig"
}

output "alarm_thresholds_configuration_profile_id" {
  value       = module.app_config["alarm_thresholds"].configuration_profile_id
  description = "Configuration profile ID for alarm thresholds AppConfig"
}

output "alarm_thresholds_appconfig_read_policy_arn" {
  value       = module.app_config["alarm_thresholds"].appconfig_read_policy_arn
  description = "IAM policy ARN for reading alarm thresholds from AppConfig"
}
