resource "aws_ssm_parameter" "splunk_hec_endpoint_app" {
  count  = local.is_primary_environment ? 1 : 0
  name   = "/${var.project}${var.environment}/app_directoryofservices_splunk_hec_endpoint"
  key_id = data.aws_kms_key.ssm_kms_key.arn
  type   = "String"
  # TODO: replace with change me ?
  value = var.splunk_hec_endpoint_app
}

# https://firehose.inputs.splunk.aws.digital.nhs.uk/services/collector/
resource "aws_ssm_parameter" "splunk_hec_endpoint_url" {
  count  = local.is_primary_environment ? 1 : 0
  name   = "/${var.project}${var.environment}/splunk_collector_url"
  key_id = data.aws_kms_key.ssm_kms_key.arn
  type   = "String"
  # TODO: replace with change me ?
  value = var.splunk_collector_url
}
