resource "aws_secretsmanager_secret" "apim_api_key" {
  # checkov:skip=CKV2_AWS_57: Temp suppression JIRA-445
  # checkov:skip=CKV_AWS_149: Temp suppression JIRA-445
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/apim-api-key"
  description = "API Key for APIM proxy"
}
