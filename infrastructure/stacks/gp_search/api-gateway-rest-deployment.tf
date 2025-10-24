resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.organization,
    aws_api_gateway_integration.status,
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
# checkov:skip=CKV_AWS_225: Caching breaks the tests
resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  stage_name  = aws_api_gateway_stage.default.stage_name
  method_path = "*/*"

  settings {
    # caching_enabled      = var.api_gateway_method_cache_enabled
    # cache_data_encrypted = true
    metrics_enabled = var.api_gateway_method_metrics_enabled

    logging_level      = var.api_gateway_logging_level
    data_trace_enabled = false

    # This is where throttling can be defined at path (or endpoint level)
    # DOSIS-2264
    throttling_burst_limit = -1
    throttling_rate_limit  = -1
  }
}
