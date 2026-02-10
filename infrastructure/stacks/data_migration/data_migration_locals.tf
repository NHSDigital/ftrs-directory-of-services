locals {
  appconfig_configuration_profile_id = try(tolist(data.aws_appconfig_configuration_profiles.appconfig_configuration_profiles.configuration_profile_ids)[0], null)
  appconfig_environment_id           = try(tolist(data.aws_appconfig_environments.appconfig_environments.environment_ids)[0], null)

  # Base table ARNs for IAM policy wildcards (stream access)
  database_table_base_arns = {
    healthcare-service = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${local.project_prefix}-database-healthcare-service${local.workspace_suffix}"
    organisation       = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${local.project_prefix}-database-organisation${local.workspace_suffix}"
    location           = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${local.project_prefix}-database-location${local.workspace_suffix}"
  }
}
