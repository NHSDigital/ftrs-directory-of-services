module "search_rest_api" {
  source = "../../modules/api-gateway-rest-api"

  rest_api_name = "${local.resource_prefix}-api-gateway"
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = module.search_rest_api.rest_api_id
  lifecycle {
    create_before_destroy = true
  }
  depends_on = [
    aws_api_gateway_method.search_get,
  ]
  triggers = {
    redeployment = sha1(jsonencode([
      module.search_rest_api
    ]))
  }
}

resource "aws_api_gateway_stage" "stage" {
  deployment_id        = aws_api_gateway_deployment.deployment.id
  rest_api_id          = module.search_rest_api.rest_api_id
  stage_name           = "default"
  xray_tracing_enabled = true
}
