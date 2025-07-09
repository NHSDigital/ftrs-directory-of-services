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

resource "aws_apigatewayv2_domain_name" "api_custom_domain" {
  domain_name = "servicesearch.${local.root_domain_name}"

  domain_name_configuration {
    certificate_arn = data.aws_acm_certificate.domain_cert.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_route53_record" "gpsearch_api_a_alias" {
  zone_id = data.aws_route53_zone.dev_ftrs_cloud.zone_id
  name    = "servicesearch.${local.root_domain_name}"
  type    = "A"
  alias {
    name                   = aws_apigatewayv2_domain_name.api_custom_domain.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.api_custom_domain.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}
