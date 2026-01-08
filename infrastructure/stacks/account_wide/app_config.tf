module "app_config" {
  source = "../../modules/app-config"

  name        = "${local.project_prefix}${local.workspace_suffix}"
  description = "AppConfig application for managing feature flags."

  use_hosted_configuration           = true
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
