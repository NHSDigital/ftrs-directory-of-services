resource "aws_api_gateway_resource" "status" {
  rest_api_id = aws_api_gateway_rest_api.api-gateway.id
  parent_id   = aws_api_gateway_rest_api.api-gateway.root_resource_id
  path_part   = "_status"
}

# Method request / response and integration request / response

# checkov:skip=CKV2_AWS_59: False positive as all endpoints are protected by mTLS
resource "aws_api_gateway_method" "status" {
  rest_api_id   = aws_api_gateway_rest_api.api-gateway.id
  resource_id   = aws_api_gateway_resource.status.id
  http_method   = "GET"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id
}

resource "aws_api_gateway_integration" "status" {
  rest_api_id             = aws_api_gateway_rest_api.api-gateway.id
  resource_id             = aws_api_gateway_resource.status.id
  http_method             = aws_api_gateway_method.status.http_method
  integration_http_method = "GET"
  type                    = "AWS"
  uri                     = module.health_check_lambda.lambda_function_invoke_arn
}

resource "aws_api_gateway_method_response" "status" {
  rest_api_id = aws_api_gateway_rest_api.api-gateway.id
  resource_id = aws_api_gateway_resource.status.id
  http_method = aws_api_gateway_method.status.http_method
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "status" {
  rest_api_id = aws_api_gateway_rest_api.api-gateway.id
  resource_id = aws_api_gateway_resource.status.id
  http_method = aws_api_gateway_method.status.http_method
  status_code = aws_api_gateway_method_response.status.status_code

  depends_on = [
    aws_api_gateway_method.status,
    aws_api_gateway_integration.status
  ]
}
