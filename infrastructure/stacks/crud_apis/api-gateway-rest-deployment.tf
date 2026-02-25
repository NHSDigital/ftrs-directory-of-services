resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_method.organization_get,
    aws_api_gateway_method.organization_post,
    aws_api_gateway_method.organization_put,
    aws_api_gateway_method.organization_proxy,
    aws_api_gateway_method.status,
    aws_api_gateway_method.healthcare_service_proxy,
    aws_api_gateway_method.location_proxy,
    aws_api_gateway_integration.organization_get,
    aws_api_gateway_integration.organization_post,
    aws_api_gateway_integration.organization_put,
    aws_api_gateway_integration.organization_proxy,
    aws_api_gateway_integration.status,
    aws_api_gateway_integration.healthcare_service_proxy,
    aws_api_gateway_integration.location_proxy,
    aws_api_gateway_gateway_response.default_gateway_response,
  ]

  rest_api_id = aws_api_gateway_rest_api.api_gateway.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.organization,
      aws_api_gateway_resource.organization_proxy,
      aws_api_gateway_resource.status,
      aws_api_gateway_resource.healthcare_service,
      aws_api_gateway_resource.healthcare_service_proxy,
      aws_api_gateway_resource.location,
      aws_api_gateway_resource.location_proxy,
      aws_api_gateway_method.organization_get,
      aws_api_gateway_method.organization_post,
      aws_api_gateway_method.organization_put,
      aws_api_gateway_method.organization_proxy,
      aws_api_gateway_method.status,
      aws_api_gateway_method.healthcare_service_proxy,
      aws_api_gateway_method.location_proxy,
      aws_api_gateway_integration.organization_get,
      aws_api_gateway_integration.organization_post,
      aws_api_gateway_integration.organization_put,
      aws_api_gateway_integration.organization_proxy,
      aws_api_gateway_integration.status,
      aws_api_gateway_integration.healthcare_service_proxy,
      aws_api_gateway_integration.location_proxy,
      aws_api_gateway_gateway_response.default_gateway_response,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  stage_name  = aws_api_gateway_stage.default.stage_name
  method_path = "*/*"

  settings {
    caching_enabled      = var.api_gateway_method_cache_enabled
    cache_data_encrypted = true
    metrics_enabled      = var.api_gateway_method_metrics_enabled

    logging_level      = var.api_gateway_logging_level
    data_trace_enabled = false

    # Throttling defined at path (or endpoint) level
    throttling_burst_limit = var.api_gateway_throttling_burst_limit
    throttling_rate_limit  = var.api_gateway_throttling_rate_limit
  }

  depends_on = [aws_cloudwatch_log_group.api_gateway_log_group]
}
