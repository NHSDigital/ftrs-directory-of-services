resource "aws_secretsmanager_secret" "apim_api_key" {
  name        = "/${local.resource_prefix}${local.workspace_suffix}/apim-api-key"
  description = "API Key for APIM proxy"
}
