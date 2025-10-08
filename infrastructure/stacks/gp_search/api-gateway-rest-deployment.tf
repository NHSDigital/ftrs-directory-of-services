resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.organization,
    aws_api_gateway_integration.status,
  ]

  rest_api_id = aws_api_gateway_rest_api.api-gateway.id

  triggers = {
    # NOTE: The configuration below will satisfy ordering considerations,
    #       but not pick up all future REST API changes. More advanced patterns
    #       are possible, such as using the filesha1() function against the
    #       Terraform configuration file(s) or removing the .id references to
    #       calculate a hash against whole resources. Be aware that using whole
    #       resources will show a difference after the initial implementation.
    #       It will stabilize to only change when resources change afterwards.
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.organization.id,
      aws_api_gateway_resource.status.id,
      aws_api_gateway_method.organization.id,
      aws_api_gateway_method.status.id,
      aws_api_gateway_integration.organization.id,
      aws_api_gateway_integration.status.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_method_settings" "all" {
  # checkov:skip=CKV2_AWS_4: False positive, we are configuring custom logging
  rest_api_id = aws_api_gateway_rest_api.api-gateway.id
  stage_name  = aws_api_gateway_stage.default.stage_name
  method_path = "*/*"

  settings {
    caching_enabled      = true
    cache_data_encrypted = true
    metrics_enabled      = true
    # Turn logging off at this level because we are configuring custom logging
    logging_level      = "OFF"
    data_trace_enabled = false

    # This is where throttling can be defined at path (or endpoint level)
    # DOSIS-2264
    throttling_burst_limit = -1
    throttling_rate_limit  = -1
  }
}
