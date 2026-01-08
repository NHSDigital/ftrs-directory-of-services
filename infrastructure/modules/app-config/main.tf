module "app_config" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-appconfig.git?ref=32f02c8ce02615e9023b05d279665e72e60c7134"

  name        = var.name
  description = var.description

  use_hosted_configuration           = var.use_hosted_configuration
  config_profile_type                = var.config_profile_type
  hosted_config_version_content_type = var.hosted_config_version_content_type
  hosted_config_version_content      = file(var.hosted_config_version_content)

  environments = var.environments
}
