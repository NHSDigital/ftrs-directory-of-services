resource "aws_api_gateway_rest_api" "api-gateway" {
  name        = "${local.resource_prefix}-api-gateway-rest${local.workspace_suffix}"
  description = var.api_gateway_description

  disable_execute_api_endpoint = false

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_request_validator" "validator" {
  name                        = "validator"
  rest_api_id                 = aws_api_gateway_rest_api.api-gateway.id
  validate_request_body       = true
  validate_request_parameters = true
}



