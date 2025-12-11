resource "aws_api_gateway_resource" "status" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  parent_id   = aws_api_gateway_rest_api.api_gateway.root_resource_id
  path_part   = "_status"
}

# Method request / response and integration request / response

resource "aws_api_gateway_method" "status" {
  # checkov:skip=CKV_AWS_59: False positive; all the endpoints will be authenticated via mTLS
  rest_api_id   = aws_api_gateway_rest_api.api_gateway.id
  resource_id   = aws_api_gateway_resource.status.id
  http_method   = "GET"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validator.id
}

resource "aws_api_gateway_integration" "status" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway.id
  resource_id             = aws_api_gateway_resource.status.id
  http_method             = aws_api_gateway_method.status.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.health_check_lambda.lambda_function_invoke_arn
}

resource "aws_api_gateway_method_response" "status" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  resource_id = aws_api_gateway_resource.status.id
  http_method = aws_api_gateway_method.status.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Content-Type"                 = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}

resource "aws_api_gateway_integration_response" "status" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway.id
  resource_id = aws_api_gateway_resource.status.id
  http_method = aws_api_gateway_method.status.http_method
  status_code = aws_api_gateway_method_response.status.status_code

  response_parameters = {
    "method.response.header.Content-Type"                 = "'application/json'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET'"
    "method.response.header.Access-Control-Allow-Headers" = "'Authorization, Content-Type, X-NHSD-REQUEST-ID, X-NHSD-CORRELATION-ID, NHSD-Message-Id, NHSD-Api-Version, NHSD-End-User-Role, NHSD-Client-Id, NHSD-Connecting-Party-App-Name'"
  }

  depends_on = [
    aws_api_gateway_method.status,
    aws_api_gateway_integration.status
  ]
}
