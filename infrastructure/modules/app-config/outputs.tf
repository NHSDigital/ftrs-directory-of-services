output "appconfig_read_policy_arn" {
  description = "ARN of the IAM policy created by the module (null if not created)."
  value       = var.create_iam_policy ? aws_iam_policy.appconfig_data_read[0].arn : null
}

output "application_id" {
  description = "The ID of the AppConfig application."
  value       = module.app_config.application_id
}

output "environment_ids" {
  description = "A map of environment IDs created in the AppConfig application."
  value       = module.app_config.environments
}

output "configuration_profile_id" {
  description = "The ID of the configuration profile in the AppConfig application."
  value       = module.app_config.configuration_profile_id
}
