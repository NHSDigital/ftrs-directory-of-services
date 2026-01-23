################################################################################
# AppConfig Integration for CloudWatch Alarm Thresholds
################################################################################
#
# DEPLOYMENT WORKFLOW:
#
# Initial Setup (One-time):
#   1. terraform apply (app_config stack) → Creates AppConfig application
#   2. terraform apply (dos_search stack)  → Reads initial config & creates alarms
#
# Ongoing Updates (No Redeployment):
#   1. Update thresholds via AWS AppConfig GUI
#   2. terraform apply (dos_search stack) → Picks up live AppConfig values
#
# How it works:
#   - AppConfig is the SOURCE OF TRUTH for alarm thresholds
#   - Terraform reads LIVE values from AppConfig (not local files)
#   - Operational teams can update AppConfig via GUI without code/Git changes
#   - Next terraform apply detects and applies changes to CloudWatch alarms
#   - Full audit trail available in both AWS AppConfig and Terraform state
#
################################################################################

# Data source to fetch LIVE alarm configuration from AppConfig
# This reads the current values stored in AWS AppConfig, not the local file
data "aws_appconfig_configuration" "alarm_thresholds" {
  application           = data.terraform_remote_state.app_config.outputs.alarm_thresholds_application_id
  environment           = data.terraform_remote_state.app_config.outputs.alarm_thresholds_environment_ids["environment"]
  configuration_profile = data.terraform_remote_state.app_config.outputs.alarm_thresholds_configuration_profile_id
  # Note: Without version_number, Terraform will fetch the LATEST version
  # This ensures Terraform always reads the most recent GUI updates
}

# Parse the live AppConfig JSON response
locals {
  # Decode the JSON content fetched from AppConfig
  alarm_config = jsondecode(data.aws_appconfig_configuration.alarm_thresholds.content)

  # Search Lambda thresholds from LIVE AppConfig
  search_lambda_duration_threshold_ms           = local.alarm_config.searchLambda.duration.threshold_ms
  search_lambda_concurrent_executions_threshold = local.alarm_config.searchLambda.concurrentExecutions.threshold
  search_lambda_errors_threshold                = local.alarm_config.searchLambda.errors.threshold
  search_lambda_invocations_threshold           = local.alarm_config.searchLambda.invocations.threshold

  # Health Check Lambda thresholds from LIVE AppConfig
  health_check_lambda_duration_threshold_ms           = local.alarm_config.healthCheckLambda.duration.threshold_ms
  health_check_lambda_concurrent_executions_threshold = local.alarm_config.healthCheckLambda.concurrentExecutions.threshold
  health_check_lambda_errors_threshold                = local.alarm_config.healthCheckLambda.errors.threshold
  health_check_lambda_invocations_threshold           = local.alarm_config.healthCheckLambda.invocations.threshold

  # Shared alarm configuration from LIVE AppConfig
  lambda_alarm_evaluation_periods = local.alarm_config.alarmConfiguration.evaluationPeriods
  lambda_alarm_period             = local.alarm_config.alarmConfiguration.periodSeconds

  # Slack notification configuration from LIVE AppConfig
  resource_prefix  = "${var.account_prefix}-${var.environment}-${var.stack_name}"
  workspace_suffix = terraform.workspace == "default" ? "" : "-${terraform.workspace}"
  common_tags = {
    Environment = var.environment
    Project     = var.project
    Stack       = var.stack_name
    Workspace   = terraform.workspace == "default" ? "default" : terraform.workspace
    ManagedBy   = "Terraform"
  }
}
