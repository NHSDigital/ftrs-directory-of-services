locals {
  appconfig_configuration_profile_id = try(data.aws_appconfig_configuration_profiles.appconfig_configuration_profiles.ids[0], null)
  appconfig_environment_id           = try(data.aws_appconfig_environments.appconfig_environments.ids[0], null)
}
