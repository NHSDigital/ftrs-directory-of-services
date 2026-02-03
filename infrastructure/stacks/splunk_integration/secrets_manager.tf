resource "aws_secretsmanager_secret" "splunk_hec_app_token" {
  count       = local.is_primary_environment ? 1 : 0
  name        = "${var.project}/${var.environment}/${var.splunk_hec_app_token_name}"
  kms_key_id  = data.aws_kms_key.secrets_manager_kms_key.arn
  description = "Splunk HTTP Event Collector token for application logging"
}

resource "aws_secretsmanager_secret_version" "splunk_hec_app_token" {
  secret_id     = aws_secretsmanager_secret.splunk_hec_app_token[0].id
  secret_string = var.splunk_hec_token_app
}
