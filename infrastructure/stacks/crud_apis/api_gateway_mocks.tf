resource "aws_apigatewayv2_route" "sandbox_org" {
  count              = var.environment == "dev" ? 1 : 0
  api_id             = module.api_gateway.api_id
  route_key          = "GET /Organization"
  target             = "integrations/${aws_apigatewayv2_integration.sandbox_org[count.index].id}"
}

resource "aws_apigatewayv2_integration" "sandbox_org" {
  count                = var.environment == "dev" ? 1 : 0
  api_id               = module.api_gateway.api_id
  integration_type     = "MOCK"
  integration_method   = "GET"
  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_route" "sandbox_org_proxy" {
  count              = var.environment == "dev" ? 1 : 0
  api_id             = module.api_gateway.api_id
  route_key          = "ANY /Organization/{proxy+}"
  target             = "integrations/${aws_apigatewayv2_integration.sandbox_org_proxy[count.index].id}"
}

resource "aws_apigatewayv2_integration" "sandbox_org_proxy" {
  count                = var.environment == "dev" ? 1 : 0
  api_id               = module.api_gateway.api_id
  integration_type     = "MOCK"
  payload_format_version = "1.0"
}
