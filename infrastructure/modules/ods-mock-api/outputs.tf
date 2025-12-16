output "ods_endpoint_url" {
  description = "Complete Mock ODS API endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.ods_mock.id}.execute-api.eu-west-2.amazonaws.com/${aws_api_gateway_deployment.ods_mock.stage_name}/organisation-data-terminology-api/fhir/Organization"
}

output "api_key_value" {
  description = "Value of the Mock ODS API key"
  value       = aws_api_gateway_api_key.ods_mock.value
  sensitive   = true
}
