resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.organization,
    aws_api_gateway_integration.status,
    aws_api_gateway_gateway_response.this,
  ]

  rest_api_id = aws_api_gateway_rest_api.api_gateway.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.organization,
      aws_api_gateway_resource.status,
      aws_api_gateway_method.organization,
      aws_api_gateway_method.status,
      aws_api_gateway_integration.organization,
      aws_api_gateway_integration.status,
      [for k in sort(keys(var.gateway_responses)) : {
        key           = k
        response_type = var.gateway_responses[k].response_type
        status_code   = var.gateway_responses[k].status_code
        template      = var.gateway_responses[k].template
      }],
      var.fhir_content_type_header,
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
}
