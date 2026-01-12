module "app_config" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-appconfig.git?ref=32f02c8ce02615e9023b05d279665e72e60c7134"

  name        = var.name
  description = var.description

  config_profile_type                = var.config_profile_type
  hosted_config_version_content_type = var.hosted_config_version_content_type
  hosted_config_version_content      = file(var.hosted_config_version_content)
  deployment_configuration_version   = local.deployment_configuration_version
  use_hosted_configuration           = local.use_hosted_configuration

  environments = var.environments
}
