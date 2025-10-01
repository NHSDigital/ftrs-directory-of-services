resource "aws_api_gateway_rest_api" "api-gateway" {
  name        = "${local.resource_prefix}-api-gateway-rest${local.workspace_suffix}"
  description = var.api_gateway_description

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}


