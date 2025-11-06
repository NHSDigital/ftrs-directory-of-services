resource "aws_api_gateway_rest_api" "api_gateway" {
  name        = "${local.resource_prefix}-api-gateway-rest${local.workspace_suffix}"
  description = var.api_gateway_description

  disable_execute_api_endpoint = true

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_request_validator" "validator" {
  name                        = "${local.resource_prefix}-api-gateway-validator${local.workspace_suffix}"
  rest_api_id                 = aws_api_gateway_rest_api.api_gateway.id
  validate_request_body       = true
  validate_request_parameters = true
}

# Single, scalable definition for all configured gateway responses
resource "aws_api_gateway_gateway_response" "this" {
  for_each      = var.gateway_responses
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  response_type = each.value.response_type
  status_code   = each.value.status_code

  response_parameters = var.fhir_content_type_header

  response_templates = {
    "application/fhir+json" = each.value.template
  }
}
