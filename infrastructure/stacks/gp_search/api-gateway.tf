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
  depends_on = [aws_cloudwatch_log_group.api_gateway_execution_logs]

  deployment_id        = aws_api_gateway_deployment.deployment.id
  rest_api_id          = module.search_rest_api.rest_api_id
  stage_name           = "default"
  xray_tracing_enabled = true
}

resource "aws_cloudwatch_log_group" "api_gateway_execution_logs" {
  name              = "/aws/apigateway/${local.resource_prefix}-api-gateway-execution-logs${local.workspace_suffix}/default"
  retention_in_days = var.retention_in_days
}

resource "aws_route53_record" "gpsearch_api_a_alias" {
  zone_id = data.aws_route53_zone.dev_ftrs_cloud.zone_id
  name    = "servicesearch.${local.root_domain_name}"
  type    = "A"
  alias {
    name                   = aws_api_gateway_stage.stage.invoke_url
    zone_id                = var.eu_west_2_api_gateway_zone_id
    evaluate_target_health = false
  }
}
