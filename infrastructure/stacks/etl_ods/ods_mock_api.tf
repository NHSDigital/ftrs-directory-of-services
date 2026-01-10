module "ods_mock_api" {
  count = contains(["dev", "test"], var.environment) ? 1 : 0

  source = "../../modules/ods-mock-api"

  api_gateway_name        = "${local.resource_prefix}-ods-mock-api${local.workspace_suffix}"
  api_gateway_description = "Mock ODS Terminology API for ETL testing in dev and test environments"
  environment             = var.environment

  throttle_burst_limit = 100
  throttle_rate_limit  = 50
  quota_limit          = 1000
}

resource "aws_ssm_parameter" "ods_mock_api_url" {
  count = contains(["dev", "test"], var.environment) ? 1 : 0

  name        = "/${local.project_prefix}/mock-api/endpoint-url${local.workspace_suffix}"
  description = "ODS Mock API endpoint URL for ETL testing"
  type        = "SecureString"
  value       = module.ods_mock_api[0].ods_endpoint_url
  key_id      = data.aws_kms_key.ssm_kms_key.arn
}

resource "aws_secretsmanager_secret" "ods_mock_api_key" {
  # checkov:skip=CKV2_AWS_57: Mock API key doesn't require automatic rotation, manual rotation is sufficient for development testing
  count = contains(["dev", "test"], var.environment) ? 1 : 0

  name        = "/${local.project_prefix}/mock-api/api-key${local.workspace_suffix}"
  description = "API key for ODS Mock API in dev and test environments"
  kms_key_id  = data.aws_kms_key.secrets_manager_kms_key.arn
}

resource "aws_secretsmanager_secret_version" "ods_mock_api_key" {
  count = contains(["dev", "test"], var.environment) ? 1 : 0

  secret_id     = aws_secretsmanager_secret.ods_mock_api_key[0].id
  secret_string = module.ods_mock_api[0].api_key_value
}
