resource "aws_secretsmanager_secret" "apim_api_key" {
  count       = local.is_primary_environment ? 1 : 0
  name        = "/${var.project}/${var.environment}/apim-api-key"
  description = "API Key for APIM proxy"
}
