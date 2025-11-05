resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.organization,
    aws_api_gateway_integration.status,
    # Ensure all gateway responses exist before deployment
    aws_api_gateway_gateway_response.this,
  ]

  rest_api_id = aws_api_gateway_rest_api.api_gateway.id

  triggers = {
    # NOTE: The configuration below will satisfy ordering considerations,
    #       but not pick up all future REST API changes. More advanced patterns
    #       are possible, such as using the filesha1() function against the
    #       Terraform configuration file(s) or removing the .id references to
    #       calculate a hash against whole resources. Be aware that using whole
    #       resources will show a difference after the initial implementation.
    #       It will stabilize to only change when resources change afterwards.
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.organization,
      aws_api_gateway_resource.status,
      aws_api_gateway_method.organization,
      aws_api_gateway_method.status,
      aws_api_gateway_integration.organization,
      aws_api_gateway_integration.status,
      # Include gateway responses to trigger redeploy on template change.
      local.gateway_responses_projection,
      # Also include response header mapping so content-type/header edits redeploy
      local.fhir_content_type_header,
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
