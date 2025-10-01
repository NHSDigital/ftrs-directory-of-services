resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.organization,
    aws_api_gateway_integration.status, # Add this line
  ]

  rest_api_id = aws_api_gateway_rest_api.api-gateway.id
  #stage_name = "dev"
}
